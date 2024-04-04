import re
import os


class SubtitleFixer:
    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = input_file + ".fixed"
        self.subtitle_entries = []

    def get_duration(self, parts):
        hour, minute, second, millisecond = map(int, parts)
        return (hour * 3600 + minute * 60 + second) * 1000 + millisecond

    def print_duration(self, duration):
        milliseconds = duration % 1000
        duration //= 1000
        seconds = duration % 60
        duration //= 60
        minutes = duration % 60
        hours = duration // 60
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def read_subtitle_entries(self):
        with open(self.input_file, "r") as file:
            lines = file.read().splitlines()

        while lines:
            # Read one subtitle entry
            idx_raw = lines.pop(0).strip()

            # Handle empty lines by skipping them
            if not idx_raw:
                continue

            try:
                idx = int(idx_raw)
            except ValueError:
                print(f"Error: Invalid subtitle index '{idx_raw}'")
                continue

            timing = re.match(
                r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", lines.pop(0)
            )
            from_time = self.get_duration(timing.groups()[:4])
            to_time = self.get_duration(timing.groups()[4:])

            content = lines.pop(0).strip()
            while lines and lines[0].strip() != "":
                content += "\n" + lines.pop(0).strip()

            self.subtitle_entries.append((idx, from_time, to_time, content))

    def fix_subtitles(self):
        new_subtitle_entries = []
        last_subtitle = None
        new_idx = 1

        for subtitle in self.subtitle_entries:
            idx, from_time, to_time, text = subtitle

            if last_subtitle is not None:
                text = text.strip()
                if len(text) == 0:
                    continue

                if to_time - from_time < 150 and last_subtitle[3] in text:
                    last_subtitle = (
                        last_subtitle[0],
                        last_subtitle[1],
                        to_time,
                        last_subtitle[3],
                    )
                    continue

                current_lines = text.split("\n")
                last_lines = last_subtitle[3].split("\n")

                if current_lines[0] == last_lines[-1]:
                    text = "\n".join(current_lines[1:])

                if from_time < last_subtitle[2]:
                    last_subtitle = (
                        last_subtitle[0],
                        last_subtitle[1],
                        from_time - 1,
                        last_subtitle[3],
                    )

                new_subtitle_entries.append(last_subtitle)
                new_idx += 1

            last_subtitle = (idx, from_time, to_time, text)

        if last_subtitle is not None:
            new_subtitle_entries.append(last_subtitle)

        # Write the fixed subtitle entries to the output file
        with open(self.output_file, "w") as new_file:
            for idx, from_time, to_time, text in new_subtitle_entries:
                new_file.write(f"{idx}\n")
                new_file.write(
                    f"{self.print_duration(from_time)} --> {self.print_duration(to_time)}\n"
                )
                new_file.write(f"{text}\n\n")

        # Rename the original file and the output file
        os.rename(self.input_file, self.input_file.replace(".srt", "_raw_subs.srt"))
        os.rename(self.output_file, self.input_file)

        print("---fixed subs---")


def fix_subs(input_file_path):
    fixer = SubtitleFixer(input_file_path)
    fixer.read_subtitle_entries()
    fixer.fix_subtitles()


if __name__ == "__main__":
    input_subtitle_file = "/tmp/youtube/uKrnx81zdnQ/uKrnx81zdnQ.srt"
    fixer = SubtitleFixer(input_subtitle_file)
    fixer.read_subtitle_entries()
    fixer.fix_subtitles()
