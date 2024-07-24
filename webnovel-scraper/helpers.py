import pandas as pd
from tabulate import tabulate
import re
import unicodedata


def select_novel(df: pd.DataFrame) -> pd.Series:
    """Prompts the user to select a novel from a DataFrame by entering a corresponding number

    Args:
        df (pd.DataFrame): A DataFrame containing novel information with an index.

    Returns:
        pd.Series: A Series containing the selected novel's information
    """

    # Get min and max of possible values
    min_value = df.index.min()
    max_value = df.index.max()

    # Ask for value from user
    selected_novel = -1
    while selected_novel > max_value or selected_novel < min_value:
        selected_novel = int(
            input("Enter the number corresponding to the novel you want to read: ")
        )
        if selected_novel > max_value or selected_novel < min_value:
            print(
                "Incorrect value, please choose a value fitting corresponding to a novel."
            )

    # Retrieve selected novel
    novel_info = df.loc[selected_novel]

    print("Selected:", novel_info.Title, "with rating", novel_info.score)
    return novel_info


def cleanChapterHeader(header1: str, header2: str) -> str:

    # Use the longer part (assuming it's more likely to contain the full title)
    main_part = max([header1, header2], key=len).strip()

    patterns = [
        r"^Chapter\s+[-]?\d+:?\s*-?\s*",  # Matches "Chapter 13:", "Chapter -2:", etc.
        r"^Chapter\s+[-]?\d+\s+",  # Matches "Chapter 13 ", "Chapter -2 ", etc.
        r"^\d+:?\s*",  # Matches "1:", "13 ", etc.
        r"^Chapter\s+",  # Matches "Chapter " at the beginning
    ]

    for pattern in patterns:
        main_part = re.sub(pattern, "", main_part, flags=re.IGNORECASE)

    return main_part.strip()


def prettyPrintTable(table: pd.DataFrame) -> None:
    """
    Prints a formatted table with selected columns from the input DataFrame.

    Parameters:
        table (pd.DataFrame): The input DataFrame containing the data to be displayed.

    Returns:
        None
    """
    newtable = table[
        ["Title", "score", "status", "Chapters", "author", "estimatedDownload"]
    ].copy(deep=True)

    # only keep main author
    newtable["author"] = newtable["author"].str.split("&").str[0]

    # more readable format
    newtable["estimatedDownload"] = (
        newtable["estimatedDownload"].round().apply(pd.to_timedelta, unit="s")
    )

    # rename columns
    newtable = newtable.rename(
        columns={
            "author": "Author",
            "estimatedDownload": "Download time (seconds)",
            "score": "Score",
            "status": "Status",
        }
    )

    print(tabulate(newtable, headers="keys", tablefmt="psql"))


def normalize_text(text: str) -> str:
    """
    Normalize the input text by removing non-ASCII characters and converting it to lowercase.

    Args:
        text (str): The text to be normalized.

    Returns:
        str: The normalized text.
    """
    # Remove non-ASCII characters and convert to lowercase
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if unicodedata.category(char) != "Mn"
    ).lower()


def remove_advertisement(text: str) -> str:
    normalized = normalize_text(text)

    # Pattern to match freewebnovel(.com) with possible obfuscation
    pattern = (
        r"f\W*r?\W*e\W*e?\W*w\W*e?\W*b?\W*n\W*o?\W*v?\W*e\W*l(\W*\.?\W*c\W*o\W*m)?"
    )
    # Find all sentences containing the pattern
    sentences = re.split(r'(?<=[.!?"])\s+', normalized)
    cleaned_sentences = []

    for sentence in sentences:
        if not re.search(pattern, normalize_text(sentence), re.IGNORECASE):
            cleaned_sentences.append(sentence)

    return " ".join(cleaned_sentences).strip()


def is_advertisement(text: str) -> bool:
    """
    Check if the given text contains any advertisement patterns.

    Args:
        text (str): The text to check for advertisement patterns.

    Returns:
        bool: True if any advertisement pattern is found, False otherwise.
    """
    normalized_text = normalize_text(text)

    # More specific patterns to match
    patterns = [
        r"\bfreewebnovel\b",
        r"visit.*for.*novel.*experience",
        r"read.*chapters.*at",
        r"content.*taken.*from",
        r"source.*of.*this.*content",
        r"updated.*from",
        r"chapter.*updated.*by",
        r"chapters.*published.*on",
        r"novels.*published.*on",
        r"follow.*current.*novels",
        r"for.*the.*best.*novel.*reading",
        r"most.*uptodate.*novels",
        r"latest.*chapters.*at",
        r"new.*novel.*chapters",
        r"free.*web.*novel",
        r"ew.*bn.*vel",
    ]

    # Check if any pattern matches
    return any(re.search(pattern, normalized_text) for pattern in patterns)
