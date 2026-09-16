"""按站点里实际出现的字裁剪字体子集，减小网页体积。

用法：
    python tools/subset-font.py                      # 用默认源字体
    python tools/subset-font.py 别的字体.ttf          # 换字体

这个字体目前只用在右上角头像的气泡上，所以只抓 .bubble 里的文字。
改过气泡文字后重新跑一次，新出现的字才会进字体文件。
"""

import glob
import os
import re
import sys

from fontTools import subset

SRC_DEFAULT = r"C:\Users\15308\Downloads\给够钱字体_字库星球\给够钱字体\给够钱_吴杨峰.ttf"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "fonts", "geigouqian.ttf")
ASCII = "".join(chr(c) for c in range(0x20, 0x7F))
SAFETY = "　，。、；：！？“”‘’（）《》——…·0123456789％"
BLOCK = re.compile(r'<div class="bubble">(.*?)</div>', re.S)
TAGS = re.compile(r"<[^>]+>")


def collect_text():
    chars = set(ASCII + SAFETY)
    for path in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        for block in BLOCK.findall(html):
            chars.update(TAGS.sub("", block))
    chars.difference_update("\n\r\t")
    return "".join(sorted(chars))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else SRC_DEFAULT
    text = collect_text()

    options = subset.Options()
    options.drop_tables += ["DSIG"]
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.notdef_outline = True
    options.recalc_bounds = True

    font = subset.load_font(src, options)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=text)
    subsetter.subset(font)

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    subset.save_font(font, DST, options)

    print("字符数：%d" % len(text))
    print("输出：%s（%d 字节）" % (DST, os.path.getsize(DST)))


if __name__ == "__main__":
    main()
