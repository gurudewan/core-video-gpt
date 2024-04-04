from pysrt import open as open_srt


def load_subtitles_text_only(file_path):

    subs = open_srt(file_path)
    raw_text = ""
    for sub in subs:
        raw_text += sub.text

    return raw_text


if __name__ == "__main__":
    load_subtitles_text_only("/tmp/youtube/5qiEdmuekL4/5qiEdmuekL4.en.srt")
