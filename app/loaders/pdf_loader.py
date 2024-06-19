
from langchain_community.document_loaders import UnstructuredFileLoader
from app.loaders.ocr import get_ocr
import cv2
from PIL import Image
import fitz
import re
import PyPDF2

from PyPDF2 import EncodingException, DecodeException
import numpy as np

PDF_OCR_THRESHOLD = (0.6, 0.6)

class PdfLoader(UnstructuredFileLoader):
    def parser(self):
        def column_boxes(page, footer_margin=50, header_margin=50, no_image_text=True):
            paths = page.get_drawings()
            bboxes = []
            path_rects = []
            img_bboxes = []
            vert_bboxes = []

            clip = +page.rect
            clip.y1 -= footer_margin
            clip.y0 += header_margin

            def can_extend(temp, bb, bboxlist):
                for b in bboxlist:
                    if not intersects_bboxes(temp, vert_bboxes) and (
                        b == None or b == bb or (temp & b).is_empty
                    ):
                        continue
                    return False
                return True

            def in_bbox(bb, bboxes):
                for i, bbox in enumerate(bboxes):
                    if bb in bbox:
                        return i + 1
                return 0

            def intersects_bboxes(bb, bboxes):
                for bbox in bboxes:
                    if not (bb & bbox).is_empty:
                        return True
                return False

            def extend_right(bboxes, width, path_bboxes, vert_bboxes, img_bboxes):
                for i, bb in enumerate(bboxes):
                    if in_bbox(bb, path_bboxes):
                        continue
                    if in_bbox(bb, img_bboxes):
                        continue
                    temp = +bb
                    temp.x1 = width
                    if intersects_bboxes(temp, path_bboxes + vert_bboxes + img_bboxes):
                        continue
                    check = can_extend(temp, bb, bboxes)
                    if check:
                        bboxes[i] = temp
                return [b for b in bboxes if b != None]

            def clean_nblocks(nblocks):
                blen = len(nblocks)
                if blen < 2:
                    return nblocks
                start = blen - 1
                for i in range(start, -1, -1):
                    bb1 = nblocks[i]
                    bb0 = nblocks[i - 1]
                    if bb0 == bb1:
                        del nblocks[i]

                y1 = nblocks[0].y1
                i0 = 0
                i1 = -1

                for i in range(1, len(nblocks)):
                    b1 = nblocks[i]
                    if abs(b1.y1 - y1) > 10:
                        if i1 > i0:
                            nblocks[i0 : i1 + 1] = sorted(
                                nblocks[i0 : i1 + 1], key=lambda b: b.x0
                            )
                        y1 = b1.y1
                        i0 = i
                    i1 = i
                if i1 > i0:
                    nblocks[i0 : i1 + 1] = sorted(nblocks[i0 : i1 + 1], key=lambda b: b.x0)
                return nblocks

            for p in paths:
                path_rects.append(p["rect"].irect)
            path_bboxes = path_rects
            path_bboxes.sort(key=lambda b: (b.y0, b.x0))
            for item in page.get_images():
                img_bboxes.extend(page.get_image_rects(item[0]))

            blocks = page.get_text(
                "dict",
                flags=fitz.TEXTFLAGS_TEXT,
                clip=clip,
            )["blocks"]

            for b in blocks:
                bbox = fitz.IRect(b["bbox"]) 
                if no_image_text and in_bbox(bbox, img_bboxes):
                    continue

                line0 = b["lines"][0]
                if line0["dir"] != (1, 0):
                    vert_bboxes.append(bbox)
                    continue

                srect = fitz.EMPTY_IRECT()
                for line in b["lines"]:
                    lbbox = fitz.IRect(line["bbox"])
                    text = "".join([s["text"].strip() for s in line["spans"]])
                    if len(text) > 1:
                        srect |= lbbox
                bbox = +srect
                if not bbox.is_empty:
                    bboxes.append(bbox)

            bboxes.sort(key=lambda k: (in_bbox(k, path_bboxes), k.y0, k.x0))
            bboxes = extend_right(
                bboxes, int(page.rect.width), path_bboxes, vert_bboxes, img_bboxes
            )

            if bboxes == []:
                return []
            nblocks = [bboxes[0]]
            bboxes = bboxes[1:]

            for i, bb in enumerate(bboxes):
                check = False
                for j in range(len(nblocks)):
                    nbb = nblocks[j]
                    if bb == None or nbb.x1 < bb.x0 or bb.x1 < nbb.x0:
                        continue
                    if in_bbox(nbb, path_bboxes) != in_bbox(bb, path_bboxes):
                        continue
                    temp = bb | nbb
                    check = can_extend(temp, nbb, nblocks)
                    if check == True:
                        break

                if not check:
                    nblocks.append(bb)
                    j = len(nblocks) - 1
                    temp = nblocks[j]

                check = can_extend(temp, bb, bboxes)
                if check == False:
                    nblocks.append(bb)
                else:
                    nblocks[j] = temp
                bboxes[i] = None

            nblocks = clean_nblocks(nblocks)
            return nblocks

        def rotate_img(img, angle):
            h, w = img.shape[:2]
            rotate_center = (w/2, h/2)
            M = cv2.getRotationMatrix2D(rotate_center, angle, 1.0)
            new_w = int(h * np.abs(M[0, 1]) + w * np.abs(M[0, 0]))
            new_h = int(h * np.abs(M[0, 0]) + w * np.abs(M[0, 1]))
            M[0, 2] += (new_w - w) / 2
            M[1, 2] += (new_h - h) / 2

            rotated_img = cv2.warpAffine(img, M, (new_w, new_h))
            return rotated_img

        def pdf2text_withOCR(filepath):
            import fitz
            import numpy as np
            ocr = get_ocr()
            doc = fitz.open(filepath)
            resp = ""

            for i, page in enumerate(doc):
                text = page.get_text("")
                resp += text + "\n"
                img_list = page.get_image_info(xrefs=True)
                for img in img_list:
                    if xref := img.get("xref"):
                        bbox = img["bbox"]
                        # 检查图片尺寸是否超过设定的阈值
                        if ((bbox[2] - bbox[0]) / (page.rect.width) < PDF_OCR_THRESHOLD[0]
                            or (bbox[3] - bbox[1]) / (page.rect.height) < PDF_OCR_THRESHOLD[1]):
                            continue
                        pix = fitz.Pixmap(doc, xref)
                        if int(page.rotation)!=0:  #如果Page有旋转角度，则旋转图片
                            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, -1)
                            tmp_img = Image.fromarray(img_array);
                            ori_img = cv2.cvtColor(np.array(tmp_img),cv2.COLOR_RGB2BGR)
                            rot_img = rotate_img(img=ori_img, angle=360-page.rotation)
                            img_array = cv2.cvtColor(rot_img, cv2.COLOR_RGB2BGR)
                        else:
                            img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, -1)

                        result, _ = ocr(img_array)
                        if result:
                            ocr_result = [line[1] for line in result]
                            resp += "\n".join(ocr_result)

            return resp
        
        def pdf2text_withoutOCR(filepath):
            try:
                count = 0
                resp = ""
                pdfFileObj = open(filepath, 'rb')
                pdfReader = PyPDF2.PdfReader(pdfFileObj, strict=False)
                num_pages = len(pdfReader.pages)
                # 无异常情况下使用PyPDF2
                """
                TODO: 产生乱码
                """
                while count < num_pages:
                    text = ""
                    pageObj = pdfReader.pages[count]
                    count += 1
                    text = pageObj.extract_text()  
                    words = "".join(text)
                    resp += words
                
                pdfFileObj.close()
                return resp
            except (EncodingException, DecodeException, UnicodeEncodeError, Exception) as e:
                # 编码异常 使用fitz
                resp = ""
                doc = fitz.open(filepath)
                for page in doc:
                    bboxes = column_boxes(page, footer_margin=50, no_image_text=True)
                    for rect in bboxes:
                        res_text = page.get_text(clip=rect, sort=True)
                        resp += res_text
                doc.close()
                return resp

        # Todo 如果是扫描件
        # text = pdf2text_withOCR(self.file_path)
        # 如果不是扫描件
        text = pdf2text_withoutOCR(self.file_path)
        return text


    def parser_with_ocr(self):
        """
        使用OCR解析pdf
        """