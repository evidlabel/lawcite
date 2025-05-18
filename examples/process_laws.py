#!/usr/bin/env python
import yaml
from pathlib import Path
from lawcite.cli.main import process_law_pdf

def main():
    """Process laws from laws.yml and save as BibTeX files in the examples directory."""
    # Get the directory of this script (examples/)
    examples_dir = Path(__file__).parent
    laws_file = examples_dir / "laws.yml"

    # Read laws.yml
    try:
        with open(laws_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {laws_file} not found")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing {laws_file}: {e}")
        return

    laws = data.get("laws", [])
    if not laws:
        print(f"No laws found in {laws_file}")
        return

    # Process each law
    for law in laws:
        name = law.get("name")
        url = law.get("url")
        if not name or not url:
            print(f"Skipping invalid entry: {law}")
            continue

        output_filename = f"{name}.bib"
        output_path = examples_dir / output_filename
        if output_path.exists():
            print(f"Skipping {name}: {output_filename} already exists")
            continue

        print(f"Processing {name} from {url}")
        try:
            process_law_pdf(
                input_url=url,
                output_filename=output_filename,
                debug=False
            )
        except Exception as e:
            print(f"Failed to process {name}: {e}")

if __name__ == "__main__":
    main()
