import turtle

screen = turtle.Screen()
screen.bgcolor("lightblue")

tree = turtle.Turtle()
tree.speed(1)
tree.color("purple")
tree.left(90)
tree.penup()
tree.goto(0, -200)
tree.pendown()

def draw_tree(branch):
    if branch < 10:
        return
    else:
        tree.forward(branch)

        tree.right(20)
        draw_tree(branch - 15)

        tree.left(40)
        draw_tree(branch - 15)

        tree.right(20)
        tree.backward(branch)

draw_tree(100)

turtle.done()