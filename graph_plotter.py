import pandas as pd


class CursedGraphs:

    def plot(self, data: list, tot_width: int = 128) -> list:
        """Takes a list of tuples, containg a label and a value."""

        # input fromat: [(label, value), (label, value), etc]

        max_value = max(count for _, count in data)
        labels_length = max([len(tup[0]) for tup in data])

        bar_width = tot_width - labels_length - 15
        increment = max_value / bar_width

        for label, count in data:

            if increment != 0:
                # Work out how wide the last chunk should be 1-8/8 block width.
                bar_chunks, remainder = divmod(int(count * 8 / increment), 8)

                # set number of full width chunks █ ░ ▓
                bar = '█' * bar_chunks

                # Then add the final fractional part by utf-code for the chars (7/8), (6/8), (5/8) etc:
                if remainder > 0:
                    bar += chr(ord('█') + (8 - remainder))
            else:
                bar = ""

            row = (
                label.rjust(labels_length),
                ' │ ',
                bar.ljust(bar_width),
                f"{count:7d} "
            )
            yield row

    def plot_grouped(self, data: list, tot_width: int = 127) -> list:
        """plots bar graphs for grouped data, like keywords per day."""

        # # # input format: [[label, value, value, etc], [label, value, value, etc], etc]

        max_value = max(count for lst in data for count in lst[1:])
        labels_length = max([len(lst[0]) for lst in data])

        bar_width = tot_width - labels_length - 12
        increment = max_value / bar_width

        for lst in data:
            label = lst[0]
            for i in range(1, 3):
                count = lst[i]

                # Work out how wide the last chunk should be 1-8/8 block width.
                if increment != 0:
                    bar_chunks, remainder = divmod(
                        int(count * 8 / increment), 8)
                    # set number of full width chunks
                    bar = '█' * bar_chunks
                    # Then add the final fractional part by utf-code for the chars (7/8), (6/8), (5/8) etc:
                    if remainder > 0:
                        bar += chr(ord('█') + (8 - remainder))
                else:
                    bar = ""

                row = (
                    label.rjust(labels_length),
                    ' │ ',
                    bar.ljust(bar_width),
                    f"{count:7d} "
                )
                yield row

    def plot_group_flex(self, data: pd.DataFrame, tot_width: int = 128) -> dict:
        """Grouped bar plotter that can take different labels for each group."""

        # # # Input data is a dataframe with top 3 categories per day, 7 last days
        data = data.head(21)
        # Establish max value to set the relative length of graph bars.
        max_value = data["count"].max()
        labels_length = data["label"].map(len).max()

        bar_width = tot_width - labels_length - 12
        increment = max_value / bar_width

        # Get a sorted list of dates to group the bars
        dates_list = sorted(list(set(data["date"].values)), reverse=True)

        # Extract data and process data, row by row
        for date in dates_list:
            current = data[(data['date'] == date)]
            row_group = {}
            row_group[date] = []
            for i in range(3):
                row_data = (current[["label", "count"]].iloc[i].values)
                label, count = row_data

                if increment == 0:  
                    # Prevent ZeroDivisionError
                    bar = ""
                else:
                    # Create the bar graphical element for the row
                    bar_chunks, remainder = divmod(
                        int(count * 8 / increment), 8)
                    # set number of full width chunks █ ░ ▓
                    bar = '█' * bar_chunks
                    # Then add the final fractional part by utf-code for the chars (7/8), (6/8), (5/8) etc:
                    if remainder > 0:
                        bar += chr(ord('█') + (8 - remainder))
                row_group[date].append([label.rjust(labels_length), " │ ", bar.ljust(bar_width), f"{int(count):7d}"])

            yield row_group