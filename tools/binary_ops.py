from typing import Dict, Any
import magic
import pefile


def binary_filetype(args: Dict[str, Any]) -> str:
    path = args.get("path")
    return magic.from_file(path, mime=True)


def binary_pe_info(args: Dict[str, Any]) -> Dict[str, Any]:
    path = args.get("path")
    pe = pefile.PE(path)
    return {
        "machine": hex(pe.FILE_HEADER.Machine),
        "number_of_sections": pe.FILE_HEADER.NumberOfSections,
        "timestamp": pe.FILE_HEADER.TimeDateStamp,
    }
