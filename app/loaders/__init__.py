import os
import chardet
import importlib
from typing import Dict

from .doc_loader import DocLoader
from .pdf_loader import PdfLoader
# from .img_loader import ImgLoader

# 其中PdfLoader、DocLoader 经重写
LOADER_DICT = {
    "UnstructuredHTMLLoader": ['.html', '.htm'],
    "UnstructuredMarkdownLoader": ['.md'],
    "JSONLoader": [".json"],
    "JSONLinesLoader": [".jsonl"],
    "CSVLoader": [".csv"],
    "PdfLoader": [".pdf"],
    "DocLoader": ['.docx', '.doc'],
    # "ImgLoader": ['.png', '.jpg', '.jpeg', '.bmp'],
    "UnstructuredFileLoader": ['.txt', '.xml'],
    "UnstructuredExcelLoader": ['.xlsx', '.xls', '.xlsd'],
    "UnstructuredPowerPointLoader": ['.ppt', '.pptx'],
}

SUPPORTED_EXTS = [ext for sublist in LOADER_DICT.values() for ext in sublist]

# 获取loader的str
def get_LoaderClass(file_extension):
    for LoaderClass, extensions in LOADER_DICT.items():
        if file_extension in extensions:
            return LoaderClass

# 获取loader
def get_loader(loader_name: str, file_path: str, loader_kwargs: Dict = None):
    loader_kwargs = loader_kwargs or {}
    try:
        if loader_name in ["PdfLoader", "DocLoader", "ImgLoader"]:
            document_loaders_module = importlib.import_module('loaders')
        else:
            document_loaders_module = importlib.import_module('langchain_community.document_loaders')
        DocumentLoader = getattr(document_loaders_module, loader_name)
    except Exception as e:
        document_loaders_module = importlib.import_module('langchain_community.document_loaders')
        DocumentLoader = getattr(document_loaders_module, "UnstructuredFileLoader")

    if loader_name == "UnstructuredFileLoader":
        loader_kwargs.setdefault("autodetect_encoding", True)
    elif loader_name == "CSVLoader":
        if not loader_kwargs.get("encoding"):
            with open(file_path, 'rb') as struct_file:
                encode_detect = chardet.detect(struct_file.read())
            if encode_detect is None:
                encode_detect = {"encoding": "utf-8"}
            loader_kwargs["encoding"] = encode_detect["encoding"]

    elif loader_name == "JSONLoader":
        loader_kwargs.setdefault("jq_schema", ".")
        loader_kwargs.setdefault("text_content", False)
    elif loader_name == "JSONLinesLoader":
        loader_kwargs.setdefault("jq_schema", ".")
        loader_kwargs.setdefault("text_content", False)

    loader = DocumentLoader(file_path, **loader_kwargs)
    return loader

# 获取文档text
def get_text(file: str) -> str:
    """
    根据文件名获取文档text
    """
    ext= os.path.splitext(file)[-1].lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"暂未支持的文件格式 {ext}")
    
    loader_name = get_LoaderClass(ext)
    loader = get_loader(loader_name, file)
    if loader_name == 'PdfLoader':
        loader = PdfLoader(file)
        return loader.parser()
    elif loader_name == 'DocLoader':
        loader = DocLoader(file)
        return loader.parser()
    # elif loader_name == 'ImgLoader':
    #     loader = ImgLoader(file)
    #     return loader._get_elements()
    else:
        docs = loader.load()
        return docs[0].page_content
