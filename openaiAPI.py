import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

import fire
import openai
from cleantext import clean
from tqdm.auto import tqdm

AVAILABLE_MODELS = [
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-0301",
    "text-davinci-003",
    "code-davinci-002",
]

logging.basicConfig(
    format="%(asctime)s | %(levelname)s: %(message)s",
    datefmt="%b/%d %H:%M:%S",
    level=logging.INFO,
)


def validate_model(model):
    """
    Validates the given model name against the list of available models.
    :param model: The name of the model to validate.
    :raises ValueError: If the given model is not in the list of available models.
    """
    if model not in AVAILABLE_MODELS:
        raise ValueError(
            f"Invalid model '{model}', available models: {', '.join(AVAILABLE_MODELS)}"
        )


def chat_generate_text(
    prompt: str,
    openai_api_key: str = None,
    model: str = "gpt-3.5-turbo",
    system_prompt: str = "You are a helpful assistant.",
    temperature: float = 1,
    max_tokens: int = 16,
    n: int = 1,
    stop: Optional[Union[str, List[str]]] = None,
    presence_penalty: float = 0,
    frequency_penalty: float = 0,
) -> List[str]:
    """
    chat_generate_text - text generation with chat-based API
    :param str prompt: _description_
    :param str openai_api_key: _description_, defaults to None
    :param str model: _description_, defaults to "gpt-3.5-turbo"
    :param float temperature: _description_, defaults to 1
    :param int max_tokens: _description_, defaults to 16
    :param int n: _description_, defaults to 1
    :param Optional[int] logprobs: _description_, defaults to None
    :param bool echo: _description_, defaults to False
    :param Optional[Union[str, List[str]]] stop: _description_, defaults to None
    :param float presence_penalty: _description_, defaults to 0
    :param float frequency_penalty: _description_, defaults to 0
    :param int best_of: _description_, defaults to 1
    :return List[str]: _description_
    """
    if openai_api_key is None:
        openai_api_key = os.environ.get("OPENAI_API_KEY", None)
    assert openai_api_key is not None, "OpenAI API key not found."

    openai.api_key = openai_api_key

    messages = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        n=n,
        stop=stop,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
    )

    generated_texts = [
        choice.message["content"].strip() for choice in response["choices"]
    ]
    return generated_texts


# UTILS


def get_timestamp():
    """
    Returns the current timestamp in the format YYYYMMDD_HHMMSS.
    :return: The current timestamp.
    """
    return datetime.now().strftime("%Y%b%d_%H-%M")


def read_and_clean_file(file_path, lower=False):
    """
    Reads the content of a file and cleans the text using the cleantext package.
    :param file_path: The path to the file.
    :return: The cleaned text.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        context = clean(f.read(), lower=lower)
    return context


def save_output_to_file(out_dir, output, file_name, prompt=None):
    """
    Saves the generated output to a file.
    :param out_dir: The output directory.
    :param output: The text to be saved.
    :param file_name: The name of the output file.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_file = out_dir / file_name

    with output_file.open("w") as f:
        f.write(output)


def main(
    prompt: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    system_prompt: str = "You are a helpful assistant.",
    temperature: float = 0.5,
    max_tokens: int = 256,
    n: int = 1,
    stop: Optional[Union[str, list]] = None,
    presence_penalty: float = 0,
    frequency_penalty: float = 0.1,
    file_path: Optional[str] = None,
    out_dir: Optional[str] = None,
    save_prompt: bool = False,
    verbose: bool = False,
):
    """
    Main function to run the text generation script.
    :param prompt: The input prompt for the model.
    :param api_key: The OpenAI API key. If not provided, checks the environment variable OPENAI_API_KEY.
    :param model: openai model code, defaults to "gpt-3.5-turbo"
    :param system_prompt: The system prompt for the model, defaults to "You are a helpful assistant."
    :param temperature: The sampling temperature (creativity) for the model.
    :param max_tokens: The maximum number of tokens in the generated text.
    :param n: The number of generated texts.
    :param stop: The stopping sequence(s) for the model.
    :param presence_penalty: The penalty applied for new token presence.
    :param frequency_penalty: The penalty applied based on token frequency.
    :param file_path: The path to a file to include as context for the prompt.
    :param out_dir: The directory to save the output text files.
    :param save_prompt: Whether to include the input prompt in the output text files.
    :param verbose: Whether to print the generated text to the console.
    """
    logger = logging.getLogger(__name__)
    openai.api_key = api_key if api_key else os.getenv("OPENAI_API_KEY")
    assert (
        openai.api_key is not None
    ), "API key not found - pass as arg or set environment variable OPENAI_API_KEY"

    prompts = []
    if file_path:
        path = Path(file_path)
        assert path.exists(), f"File {file_path} does not exist."
        logger.info(f"Reading file {file_path}...")
        if path.is_file():
            with open(path, "r") as f:
                content = f.read()
            prompts.append(prompt + "\n" + content)
        elif path.is_dir():
            for file in path.glob("*.txt"):
                with open(file, "r") as f:
                    content = f.read()
                prompts.append(prompt + "\n" + content)
        logger.info(f"read text from {len(prompts)} prompts.")
    else:
        logger.info(f"No file path provided, using prompt:\t{prompt}")
        prompts.append(prompt)

    assert len(prompts) > 0, "No prompts found."
    validate_model(model)

    logger.info(f"Generating text for {len(prompts)} prompts using model:\t{model}...")
    for i, modified_prompt in enumerate(tqdm(prompts, desc="Generating text"), start=1):
        generated_texts = chat_generate_text(
            prompt=modified_prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            n=n,
            stop=stop,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )

        if out_dir:
            out_path = Path(out_dir)
            out_path.mkdir(parents=True, exist_ok=True)
        ts = get_timestamp()
        for j, text in enumerate(generated_texts, start=1):
            if verbose or not out_dir:
                print(f"Result {j}:\n{text}")
            if out_dir:
                output_content = f"{modified_prompt}\n{text}" if save_prompt else text
                output_file = out_path / f"result_{i}_{ts}_{j}.txt"
                with open(output_file, "w") as f:
                    f.write(output_content)
    # write the parameters to a file if out_dir is provided
    if out_dir:
        with open(out_path / "generation_params.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "prompt": prompt,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "n": n,
                    "stop": stop,
                    "presence_penalty": presence_penalty,
                    "frequency_penalty": frequency_penalty,
                    "file_path": file_path,
                },
                f,
                indent=4,
            )


if __name__ == "__main__":
    fire.Fire(main)