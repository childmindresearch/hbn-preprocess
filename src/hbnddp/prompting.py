"""Prompts user for interactive data filtering."""

from pathlib import Path

import questionary

certainties = ["Confirmed", "Presumptive", "RC", "RuleOut", "ByHx", "Unknown"]


class Interactive:
    """Class for prompting user interactively."""

    @staticmethod
    def _get_paths() -> tuple[str, str]:
        """Prompts user for input path."""
        input_path = questionary.path(
            message="Please enter the path to the HBN data file.",
            default="./data/",
        ).ask()
        while not Path(input_path).exists():
            print(f"File {input_path} not found.")
            input_path = questionary.path(
                message="Please enter the path to the HBN data file.",
                default="./data/",
            ).ask()
        while not input_path.endswith(".csv"):
            print("File must be a CSV.")
            input_path = questionary.path(
                message="Please enter the path to the HBN data file.",
                default="./data/",
            ).ask()
        output_path = questionary.path(
            message="Please enter the output path to save the processed data.",
            default=input_path.replace(".csv", "_processed.csv"),
        ).ask()
        while output_path is None or not Path(output_path).parent.exists():
            if output_path is None:
                print("Output path cannot be empty.")
            else:
                print(f"Directory {str(Path(output_path).parent)} not found.")
            output_path = questionary.path(
                message="Please enter the output path to save the processed data.",
                default=input_path.replace(".csv", "_processed.csv"),
            ).ask()
        return input_path, output_path

    @staticmethod
    def _get_pivot_by() -> str:
        """Prompts user for how to pivot the data."""
        questions = [
            {
                "type": "select",
                "name": "pivot_by",
                "message": "How would you like to pivot the data?",
                "choices": [
                    "diagnoses",
                    "subcategories",
                    "categories",
                    "all",
                ],
            }
        ]
        return questionary.prompt(questions)["pivot_by"]

    @staticmethod
    def _data_filter(**kwargs: object) -> dict:
        """Prompts user for filtering."""
        print(
            "The HBN dataset includes diagnoses with varying levels of diagnostic "
            "certainty. \n If a clinician was not able to confirm a diagnosis, "
            "but symptoms were endorsed, they may refer families to follow up or seek "
            "further testing. \n\n"
            "Possible diagnostic certainties in the dataset include: "
            "confirmed, presumptive, requires confirmation (RC), rule out, and by "
            "history (ByHx). \n\n"
            "The dataset also indicates the time course of diagnoses - past or present."
            "\n \n"
        )
        url = "https://fcon_1000.projects.nitrc.org/indi/cmi_healthy_brain_network/Phenotypic.html#Diagnosis"
        text = "HBN Diagnostic Process"
        hyperlink = f"\x1b]8;;{url}\x1b\\{text}\x1b]8;;\x1b\\"
        questionary.print(
            "To learn more about diagnostic certainties and the HBN "
            "dataset as a whole, click here:",
            style="fg:orange bold",
        )
        print("\033[1m" + "\33[93m" f"{hyperlink}")

        questions = [
            {
                "type": "confirm",
                "name": "apply_filter",
                "message": "Filter the data by diagnostic certainty?",
                "default": True,
            },
            {
                "type": "checkbox",
                "name": "certainty_filter",
                "message": "Please select which diagnoses should be included in the "
                "dataset based on their certainties.",
                "choices": certainties,
                "when": lambda x: x["apply_filter"],
                "validate": lambda a: (
                    True if len(a) > 0 else "You must select at least one option."
                ),
            },
        ]
        return questionary.prompt(questions, **kwargs)

    @staticmethod
    def _include_details() -> bool:
        """Prompts user for whether to include details."""
        questions = [
            {
                "type": "confirm",
                "name": "include_details",
                "message": "You have selected to pivot the data by higher level "
                "categories rather than specific diagnoses. Would you like to include "
                "diagnosis level details in the output?",
                "default": False,
            }
        ]
        return questionary.prompt(questions)["include_details"]

    @staticmethod
    def _visualize() -> bool:
        """Prompts user for how to visualize the data."""
        questions = [
            {
                "type": "confirm",
                "name": "visualize",
                "message": "Would you like to visualize the data?",
                "default": True,
            }
        ]
        return questionary.prompt(questions)["visualize"]

    @staticmethod
    def _get_filter_args(resp: dict) -> list | None:
        """Returns parameters to use in pivot function."""
        if resp["apply_filter"]:
            certainty_filter = resp["certainty_filter"]
        else:
            certainty_filter = None
        return certainty_filter

    @staticmethod
    def prompt() -> dict:
        """Runs the interactive prompts."""
        input_path, output_path = Interactive._get_paths()
        by = Interactive._get_pivot_by()
        if by == "categories":
            include_details = Interactive._include_details()
        else:
            include_details = False
        certainty_filter = Interactive._get_filter_args(Interactive._data_filter())
        viz = Interactive._visualize()
        return {
            "input_path": input_path,
            "output_path": output_path,
            "by": by,
            "certainty_filter": certainty_filter,
            "include_details": include_details,
            "viz": viz,
        }
