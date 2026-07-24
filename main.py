import sys
import os
import argparse
from src.converter import UnstructuredConverter

def main():
    parser = argparse.ArgumentParser(
        description="Unstructured File Converter - Convert unstructured documents (PDF, DOCX, HTML, TXT, CSV, Images) to MD and JSON.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Subcommands")

    # Single file conversion command
    file_parser = subparsers.add_parser("convert", help="Convert a single file")
    file_parser.add_argument("input_file", help="Path to input unstructured file")
    file_parser.add_argument("-o", "--output-dir", default="./output", help="Directory to save output MD and JSON files (default: ./output)")

    # Batch conversion command
    batch_parser = subparsers.add_parser("convert-batch", help="Convert a folder of files")
    batch_parser.add_argument("input_dir", help="Directory containing unstructured files")
    batch_parser.add_argument("-o", "--output-dir", default="./output", help="Directory to save converted files")
    batch_parser.add_argument("-r", "--recursive", action="store_true", help="Search input directory recursively")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    converter = UnstructuredConverter()

    if args.command == "convert":
        print(f"[FILE] Processing input file: {args.input_file}")
        try:
            md_path, json_path, doc = converter.convert_file(args.input_file, args.output_dir)
            print("==================================================")
            print("[SUCCESS] CONVERSION COMPLETED")
            print(f"   * Document Title: {doc.title}")
            print(f"   * File Type:      {doc.metadata.file_type}")
            print(f"   * Word Count:     {doc.metadata.word_count}")
            print(f"   * Markdown File:  {os.path.abspath(md_path)}")
            print(f"   * JSON AST File:  {os.path.abspath(json_path)}")
            print("==================================================")
        except Exception as e:
            print(f"[ERROR] Failed to convert file: {e}")
            sys.exit(1)

    elif args.command == "convert-batch":
        print(f"[DIR] Processing directory: {args.input_dir} (Recursive: {args.recursive})")
        results = converter.convert_batch(args.input_dir, args.output_dir, recursive=args.recursive)
        success_count = sum(1 for r in results if r["status"] == "success")
        fail_count = len(results) - success_count

        print("==================================================")
        print("[SUMMARY] BATCH CONVERSION RESULTS")
        print(f"   * Total Files Processed: {len(results)}")
        print(f"   * Successful:           {success_count}")
        print(f"   * Failed:               {fail_count}")
        print(f"   * Output Directory:     {os.path.abspath(args.output_dir)}")
        print("==================================================")
        for r in results:
<<<<<<< HEAD
            if r["status"] == "successed":
=======
            if r["status"] == "successful":
>>>>>>> feature/config-update
                print(f"  + {r['filename']} -> MD & JSON ({r['word_count']} words)")
            else:
                print(f"  - {r['file']} -> {r['error']}")

if __name__ == "__main__":
    main()
