# NUMBER PATTERNS IN PYTHON
# ==========================
# Collection of beginner-friendly number pattern programs.
# Change n in any section to try different sizes.


# 1. Continuous Number Triangle Pattern
# Output:
# 1
# 1 2
# 1 2 3
# 1 2 3 4
# 1 2 3 4 5

print("\n1. Continuous Number Triangle Pattern")
n = 5

for i in range(1, n + 1):
    print(" ".join(str(x) for x in range(1, i + 1)))


# 2. Inverted Right-Angled Number Triangle Pattern
# Output:
# 1 2 3 4 5
# 1 2 3 4
# 1 2 3
# 1 2
# 1

print("\n2. Inverted Right-Angled Number Triangle Pattern")
n = 5

for i in range(n, 0, -1):
    print(" ".join(str(x) for x in range(1, i + 1)))


# 3. Centered Pyramid of Numbers Pattern
# Output:
#         1
#       1 2
#     1 2 3
#   1 2 3 4
# 1 2 3 4 5

print("\n3. Centered Pyramid of Numbers Pattern")
n = 5

for i in range(1, n + 1):
    spaces = " " * (n - i)
    numbers = " ".join(str(x) for x in range(1, i + 1))
    print(spaces + numbers)


# 4. Hollow Square with Numbers Pattern
# Output:
# 1 2 3 4 5
# 1       5
# 1       5
# 1       5
# 1 2 3 4 5

print("\n4. Hollow Square with Numbers Pattern")
n = 5

for i in range(1, n + 1):
    row = ""

    for j in range(1, n + 1):
        if i == 1 or i == n or j == 1 or j == n:
            row += str(j) + " "
        else:
            row += "  "

    print(row.rstrip())


# 5. Floyd's Triangle Number Pattern
# Output:
# 1
# 2 3
# 4 5 6
# 7 8 9 10
# 11 12 13 14 15

print("\n5. Floyd's Triangle Number Pattern")
n = 5
num = 1

for i in range(1, n + 1):
    row = []

    for _ in range(i):
        row.append(str(num))
        num += 1

    print(" ".join(row))


# 6. Palindromic Triangle Number Pattern
# Output:
#         1
#       2 1 2
#     3 2 1 2 3
#   4 3 2 1 2 3 4
# 5 4 3 2 1 2 3 4 5

print("\n6. Palindromic Triangle Number Pattern")
n = 5

for i in range(1, n + 1):
    spaces = " " * (2 * (n - i))
    left = " ".join(str(x) for x in range(i, 0, -1))
    right = " ".join(str(x) for x in range(2, i + 1))

    print(spaces + left + (" " + right if right else ""))


# 7. Alternating Ascending & Descending Number Pattern
# Output:
# 1
# 2 1
# 1 2 3
# 4 3 2 1
# 1 2 3 4 5

print("\n7. Alternating Ascending & Descending Number Pattern")
n = 5

for i in range(1, n + 1):
    if i % 2 == 0:
        row = " ".join(str(x) for x in range(i, 0, -1))
    else:
        row = " ".join(str(x) for x in range(1, i + 1))

    print(row)


# 8. Number Diamond Pattern
# Output:
#         1
#       1 2
#     1 2 3
#   1 2 3 4
# 1 2 3 4 5
#   1 2 3 4
#     1 2 3
#       1 2
#         1

print("\n8. Number Diamond Pattern")
n = 5

# Upper part
for i in range(1, n + 1):
    spaces = " " * (n - i)
    numbers = " ".join(str(x) for x in range(1, i + 1))
    print(spaces + numbers)

# Lower part
for i in range(n - 1, 0, -1):
    spaces = " " * (n - i)
    numbers = " ".join(str(x) for x in range(1, i + 1))
    print(spaces + numbers)