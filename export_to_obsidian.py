import json
import argparse
import os
import time
from pathlib import Path
from tqdm import tqdm
import uuid
from datetime import datetime
import re

root = Path(__file__).parent

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--input", type=str, default=(root / "out" / "output.json").as_posix(), help="input papger json file")
  parser.add_argument("--output", type=str, default=(root / "out" / "obsidian").as_posix(), help="output obsidian md notes folder")
  args = parser.parse_args()

  output_dir = Path(args.output)
  output_dir.mkdir(exist_ok=True)
  
  # load paper data
  with open(args.input, "r") as f:
    papers = json.load(f)
  
  for i, paper in enumerate(papers.values()):
    if "ExportToObsidian" in paper and paper["ExportToObsidian"] == 1:
      print(paper)
      file_name = paper["title"]
      invalid_chars = r'\/:*?"<>|'  # Invalid characters for file name
      for char in invalid_chars:
        file_name = file_name.replace(char, '')
      
      with open(os.path.join(args.output, f"{file_name}.md"), "w") as f:
        uid = str(uuid.uuid4())
        data_str = datetime.today().strftime('%Y-%m-%d')
        abstract_str = paper["abstract"]
        
        # Regex pattern to match the leading ArXiv ID and the following text
        pattern = r"^arXiv:[\d.]+v\d+\s+Announce Type:\s+new\s+Abstract:\s*"
        # Remove the leading portion
        abstract_str = re.sub(pattern, "", abstract_str)

        # Regex pattern to find URLs
        url_pattern = r'https?://[^\s]+'
        # Extracting the URL
        urls = re.findall(url_pattern, abstract_str)
        
        paper_string = '---\n'
        paper_string += f"uid: {uid}\n"
        paper_string += 'timesViewed: 1\n'
        paper_string += r'date created: <% tp.file.creation_date("YYYY-MM-DD\THH:mm:ss") %>'
        paper_string += '\n'
        paper_string += r'date modified: <% tp.file.last_modified_date() %>'
        paper_string += '\n'
        paper_string += f"title: {file_name}\n"
        paper_string += 'dg-publish: false\n'
        paper_string += 'aliases:\n'
        paper_string += '---\n\n'

        paper_string += '### Tags\n#area/AI #arxiv #GptPaperAssistant\n\n'
        paper_string += '### Links\n\n'
        paper_string += f"### [{file_name}]()\n\n"
        paper_string += f"### Date Added: {data_str}\n\n"
        paper_string += f"### Paper link \n[{file_name}](https://arxiv.org/abs/{paper['arxiv_id']})\n\n"        
        if len(urls) > 0 and 'github' in urls[0]:
          paper_string += f"### Github repo \n[{file_name}]({urls[0].rstrip('.,}')})\n\n"        

        paper_string += '### Abstract\n'
        paper_string += f"{abstract_str}"
  
        f.write(paper_string)
        
    