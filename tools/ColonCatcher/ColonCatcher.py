
# Colon Locater and Reporter, by RemieRichards V1.0 - 25/10/15

# Locates the byond operator ":", which is largely frowned upon due to the fact it ignores any type safety.
# This tool produces a .txt of "filenames line,line?,line totalcolons" (where line? represents a colon in a ternary operation) from all
# .dm files in the /code directory of an SS13 codebase, but can work on any Byond project if you modify scan_dir and real_dir
# the .txt take's todays date in reverse order and adds -colon_operator_log to the end, eg: "2015/10/25-colon_operator_log.txt"

import sys
import os
from datetime import date


#Climbs up from /tools/ColonCatcher and along to ../code
scan_dir = "code" #used later to truncate log file paths
real_dir = os.path.abspath(f"../../{scan_dir}")


#Scan a directory, scanning any dm files it finds
def colon_scan_dir(scan_dir):
    if os.path.exists(scan_dir):
        if os.path.isdir(scan_dir):

            output_str = ""

            files_scanned = 0
            files_with_colons = 0
            for root, dirs, files in os.walk(scan_dir):
                for f in files:
                    print str(f)
                    scan_result = scan_dm_file(os.path.join(root, f))
                    files_scanned += 1
                    if scan_result:
                        output_str += scan_result+"\n"
                        files_with_colons += 1
            output_str += str(files_with_colons) + "/" + str(files_scanned) + " files have colons in them"

            todays_file = str(date.today())+"-colon_operator_log.txt"
            output_file = open(todays_file, "w") #w so it overrides existing files for today, there should only really be one file per day
            output_file.write(output_str)



#Scan one file, returning a string as a "report" or if there are no colons, False
def scan_dm_file(_file):
    
    if not _file.endswith(".dm"):
        return False

    with open(_file, "r") as dm_file:
        characters = dm_file.read()

        line_num = 1
        colon_count = 0
        last_char = ""

        in_embed_statement = 0        # [ ... ]  num due to embeds in embeds
        in_multiline_comment = 0      #/* ... */ num due to /* /* */ */
        in_singleline_comment = False #// ... \n 
        in_string = False             # " ... "
        ternary_on_line = False       #If there's a ? anywhere on the line, used to report "false"-positives

        lines_with_colons = []

        for char in characters:
            if char in ["\n", "\r"]:
                if not in_string:
                    ternary_on_line = False #Stop any old ternary operation
                    line_num += 1
                    in_embed_statement = 0

            #Not in a comment
            if (not in_singleline_comment) and (in_multiline_comment == 0):
                #Not in a string
                if not in_string:
                    if char == "*":
                        if last_char == "/":
                            in_multiline_comment += 1
                    elif char == "/":
                        if last_char == "/":
                            in_singleline_comment = True
                    elif char == "\"":
                        in_string = True

                else:
                    if char == "[":
                        in_embed_statement += 1
                    elif char == "]":
                        in_embed_statement -= 1
                        in_embed_statement = max(in_embed_statement,0)

                    elif char == "\"":
                        if last_char != "\\": #make sure it's a real " not an escaped one (\")
                            in_string = False

                #ternary statements, True when in_embed_statement+in_string OR when not in_string
                if char == ":":
                    if in_string and in_embed_statement != 0 or not in_string:
                        colon_count += 1
                        data = str(line_num)
                        if ternary_on_line:
                            data += "?"
                        if not data in lines_with_colons:
                            lines_with_colons.append(data)

                elif char == "?":
                    if in_string and in_embed_statement != 0 or not in_string:
                        ternary_on_line = True
            else:
                if char == "/":
                    if last_char == "*":
                        in_multiline_comment -= 1
                        in_multiline_comment = max(in_multiline_comment,0)

                if char in ["\n", "\r"]:
                    in_singleline_comment = False


            if char != "": #Spaces aren't useful to us
                last_char = char


        if colon_count:
            file_report = f"..{scan_dir}{str(_file).split(scan_dir)[1]}" + " "

            first = True
            for line in lines_with_colons:            
                if first:
                    first = False
                    file_report += "Lines: "+line
                else:
                    file_report += ", "+line

            file_report += " Total Colons: "+str(colon_count)
            return file_report
        else:
            return False


        
colon_scan_dir(real_dir)
print "Done!"
