import turtle
import math

screen = turtle.Screen()
screen.setup(width=700, height=700)
screen.bgcolor("black")
screen.title("I love you!")

t = turtle.Turtle()
t.hideturtle()
t.width(2)

def heart(scale, color):
    t.penup()
    t.goto(0, -10)
    t.pendown()
    t.color(color)
    t.begin_fill()
    for i in range(360):
        x = scale * 16 * math.sin(math.radians(i)) ** 3
        y = scale * (
            13 * math.cos(math.radians(i))
            - 5 * math.cos(2 * math.radians(i))
            - 2 * math.cos(3 * math.radians(i))
            - math.cos(4 * math.radians(i))
        )
        t.goto(x, y)
    t.end_fill()

screen.tracer(0)
heart(18, "#330000")
screen.update()

screen.tracer(1)
heart(14, "#ff1a1a")

t.penup()
t.goto(0, -150)
t.color("#fffefe")
try:
    t.write("I love you \u2764", align="center",
            font=("Segoe UI", 22, "bold"))
except Exception:
    t.write("I love you <3", align="center",
            font=("Segoe UI", 22, "bold"))
    
turtle.done()