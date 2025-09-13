import os
import sys

SUFFIX = ".下载"

def remove_download_suffix(js_folder: str):
    if not os.path.isdir(js_folder):
        print(f"目录不存在: {js_folder}")
        return

    renamed = 0
    skipped = 0

    for root, _, files in os.walk(js_folder):
        for fname in files:
            if not fname.endswith(SUFFIX):
                continue

            src = os.path.join(root, fname)
            new_name = fname[: -len(SUFFIX)]
            dst = os.path.join(root, new_name)

            # 冲突处理：目标已存在则加 (1), (2)...
            if os.path.exists(dst):
                name_no_ext, ext = os.path.splitext(new_name)
                i = 1
                while True:
                    candidate = os.path.join(root, f"{name_no_ext} ({i}){ext}")
                    if not os.path.exists(candidate):
                        dst = candidate
                        break
                    i += 1
                skipped += 1  # 统计下发生过冲突的情况

            try:
                os.rename(src, dst)
                print(f"重命名: {src} -> {dst}")
                renamed += 1
            except Exception as e:
                print(f"重命名失败: {src} -> {dst}，错误：{e}")

    print(f"处理完成：重命名 {renamed} 个文件（其中 {skipped} 个发生重名冲突已加序号）。")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    js_folder = os.path.join(base_dir, "js")
    # 支持传入自定义目录：python test.py D:\path\to\js
    if len(sys.argv) > 1:
        js_folder = sys.argv[1]
    remove_download_suffix(js_folder)