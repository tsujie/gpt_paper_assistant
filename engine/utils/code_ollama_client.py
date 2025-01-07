import os
import json
import time
from pathlib import Path

from engine.constants import MAX_TOKENS, TEMPERATURE, NUM_COMPLETIONS
import ollama

class OLlamaClient:
    def __init__(self, model_name="nezahatkorkmaz/deepseek-v3", cache="ollama_cache.json"):
        self.cache_file = cache
        self.model_name = model_name

        # Load cache
        if os.path.exists(cache):
            while os.path.exists(self.cache_file + ".tmp") or os.path.exists(self.cache_file + ".lock"):
                time.sleep(0.1)
            with open(cache, "r") as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

        # Load model and tokenizer
        print("Loading tokenizer and model...")
        load_start = time.time()
        load_end = time.time()
        print(f"Model loading time: {load_end - load_start:.2f} seconds")

    def generate(self, user_prompt, system_prompt, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, stop_sequences=None, verbose=False,
                 num_completions=NUM_COMPLETIONS, skip_cache_completions=0):
        
        print(f'[INFO] OLlama: querying for {num_completions=}, {skip_cache_completions=} before searching cache')
        if verbose:
            print(user_prompt)
            print("-----")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        cache_key = str((user_prompt, system_prompt, max_tokens, temperature, stop_sequences, 'ollama'))

        num_completions = skip_cache_completions + num_completions
        if cache_key in self.cache:
            print(f'[INFO] OLlama: cache hit {len(self.cache[cache_key])}')
            if len(self.cache[cache_key]) < num_completions:
                num_completions -= len(self.cache[cache_key])
                results = self.cache[cache_key]
            else:
                return cache_key, self.cache[cache_key][skip_cache_completions:num_completions]
        else:
            results = []

        print(f'[INFO] OLlama: querying for {num_completions=}')

        while num_completions > 0:
            response = ollama.generate(model=self.model_name, prompt=user_prompt, system=system_prompt)
            #results.append(response['response'].split('\n'))
            results.append(response['response'])
            num_completions -= 1

        self.update_cache(cache_key, results)
        return cache_key, results[skip_cache_completions:]

    def update_cache(self, cache_key, results):
        while os.path.exists(self.cache_file + ".tmp") or os.path.exists(self.cache_file + ".lock"):
            time.sleep(0.1)
        with open(self.cache_file + ".lock", "w") as f:
            pass
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                self.cache = json.load(f)
        self.cache[cache_key] = results
        with open(self.cache_file + ".tmp", "w") as f:
            json.dump(self.cache, f)
        os.rename(self.cache_file + ".tmp", self.cache_file)
        os.remove(self.cache_file + ".lock")

def setup_ollama():
    try:
        username = os.getlogin()
    except OSError:
        username = os.environ.get('USER') or os.environ.get('LOGNAME')

    model = OLlamaClient(cache='ollama_cache.json' if not os.path.exists('/viscam/') else f'ollama_cache_{username}.json')
    return model
