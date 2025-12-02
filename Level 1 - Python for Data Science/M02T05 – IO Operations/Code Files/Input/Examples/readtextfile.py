# =========== Encoding Files =========== #

# When you run the unencoded example you may notice that the output
# displays strange characters.
# This can be fixed by specifying the encoding scheme,
# UTF-8 or UTF-8-SIG, as an additional argument to the open() function.
# utf-8-sig is a variation of the utf-8 encoding that
# includes a Byte Order Mark (BOM) at the beginning of the file.
# The BOM is a special marker that indicates the file is UTF-8 encoded.
# By using utf-8-sig, you can avoid the appearance
# of strange characters at the beginning of the text,
# as the BOM is properly handled.
# When you run the encoded example, using utf-8-sig,
# you will notice that the data is transformed so that
# it is compatible for reading.


# Unencoded example
print("\n--Unencoded Example--\n")

# Open 'example.txt' in read mode without specifying encoding
with open("example.txt", "r") as file:
    # Read all lines from the file into 'lines'
    lines = file.readlines()

# Print the lines read from the file
print(lines)

# Encoded example using utf-8
print("\n--Encoded Example using utf-8--\n")

# Open 'example.txt' in read mode with utf-8 encoding
with open("example.txt", "r", encoding="utf-8") as file:
    # Read all lines from the file into 'lines'
    lines = file.readlines()

# Print the lines read from the file
print(lines)  # Note: utf-8 does not include a Byte Order Mark (BOM) by default

# Encoded example using utf-8-sig
print("\n--Encoded Example using utf-8-sig--\n")

# Open 'example.txt' in read mode with utf-8-sig encoding
with open("example.txt", "r", encoding="utf-8-sig") as file:
    # Read all lines from the file into 'lines'
    lines = file.readlines()

# Print the lines read from the file
print(lines)  # Note: utf-8-sig includes a Byte Order Mark (BOM)
