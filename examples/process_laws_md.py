#!/usr/bin/env python
from pathlib import Path
from lawcite.cli.main import process_law_pdf


def main():
    """Process common Danish laws and save as Markdown files in the examples directory."""
    # Get the directory of this script (examples/)
    examples_dir = Path(__file__).parent

    # List of laws: name and URL
    laws = [
        {
            "name": "konkurrenceloven",
            "url": "https://www.retsinformation.dk/api/pdf/244970",
        },
        {
            "name": "forældreansvarsloven",
            "url": "https://www.retsinformation.dk/api/pdf/217344",
        },
        {
            "name": "retssikkerhedsloven",
            "url": "https://www.retsinformation.dk/api/pdf/248072",
        },
        {
            "name": "retsplejeloven",
            "url": "https://www.retsinformation.dk/api/pdf/245119",
        },
        {
            "name": "straffeloven",
            "url": "https://www.retsinformation.dk/api/pdf/244983",
        },
        {
            "name": "barnetslov",
            "url": "https://www.retsinformation.dk/api/pdf/248080",
        },
        {
            "name": "serviceloven",
            "url": "https://www.retsinformation.dk/api/pdf/248083",
        },
    ]

    # Process each law
    for law in laws:
        name = law["name"]
        url = law["url"]
        output_filename = f"{name}.md"
        output_path = examples_dir / output_filename
        if output_path.exists():
            print(f"Skipping {name}: {output_filename} already exists")
            continue

        print(f"Processing {name} from {url}")
        try:
            process_law_pdf(input_url=url, output_filename=output_filename, debug=False)
        except Exception as e:
            print(f"Failed to process {name}: {e}")


if __name__ == "__main__":
    main()
