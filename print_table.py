
# this is not perfect but i wrote it myself to help print cursor as a table
# [IMPORTANT!] terminal width has to be as large as the table itself
# refuce the font size if the table donesn't fit all in
# n = how many rows to print
# space_px = padding for the table in charaters as pixels
# separate_header = None(built in), False or list with header
def print_table(cur, space_px = 1, n = None, separate_header = None):

    header_table = []
    if type(cur) == list and separate_header != None:
        header_table = separate_header

    # creating a table as list of tuples
    table = []
    for row in cur:
        table.append(row)

    # dictionary to hold each column's max width
    col_widths = {}


    # figure out each row's width
    for i,row in enumerate(table):
        for i,cell in enumerate(row):
            # adding the header to the list if not there yet
            if type(cell) == float:
                cell = round(cell,1)
            cell = str(cell)

            if len(cell) > 15:
                cell = cell[:15]+"..."

            try:
                header = str(cur.description[i][0])
                if header not in header_table:
                    header_table.append(cur.description[i][0])
            except:
                if separate_header != None:
                    header = str(header_table[i])

                else:
                    header = cell

            # calculation of widths
            cell_width = len(cell) + space_px*2
            head_width = len(header) + space_px*2

            # if this is the first time - use header width as a starter
            if i not in col_widths.keys():
                col_widths[i] = head_width
            # if head_width was too short - we'll replace it with cell_width
            if cell_width > col_widths[i]:
                col_widths[i] = cell_width

    # print header
    if separate_header != False:
        # figuring out how long should the header line be
        line = ''
        for row in col_widths.values():
            line += "-"*row + "-"*3
        print("\n"+line)
        # now printing the header items form header_table
        for i, cell in enumerate(header_table):
            try:
                space_after_px = col_widths[i] - space_px - len(str(cell))
            except:
                print("\n# WARNING: Looks like header has more rows than the table!")
            # print("i is {} and last key is {}".format(i, list(col_widths.keys())[-1]))
            if i == list(col_widths.keys())[-1]:
                str_after = "\n"
            else:
                str_after = " "*space_after_px + " |"
            str_before = " "*space_px
            print(str_before, cell, end = str_after)
        # printing final bottom line
        print(line)
    else:
        print("no header")


    # print the table
    for row in table[:n]:
        for i,cell in enumerate(row):
            if type(cell) == float:
                cell = round(cell,1)
            if len(str(cell)) > 15:
                cell = str(cell)[:15]+"..."

            space_after_px = col_widths[i] - space_px - len(str(cell))
            if i == list(col_widths.keys())[-1]:
                str_after = "\n"
            else:
                str_after = " "*space_after_px + " |"

            str_before = " "*space_px
            print(str_before, cell,  end = str_after)
        print(end = "")

    # for debugging purposes
    # print(col_widths)
