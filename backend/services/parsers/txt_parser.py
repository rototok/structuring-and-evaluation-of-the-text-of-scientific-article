from chardet import UniversalDetector


def detect_encoding(file_name: str) -> str:
    detector = UniversalDetector()

    with open(file_name, mode="rb") as file:
        for line in file:
            detector.feed(line)
            if detector.done:
                break
    
    detector.close()
    
    encoding = detector.result['encoding']

    return encoding


def parse_txt(file_name: str) -> str:
    encoding = detect_encoding(file_name)

    with open(file_name, mode="r", encoding=encoding) as txt_file:
        text = txt_file.read()

    text = text.strip()
    
    return text