
import glfw
from OpenGL.GL import *
import numpy as np
import math
import sys

class MinBiggerThanMaxError(Exception):
    def __init__(self):
        super().__init__("Min값이 Max값보다 큽니다.")


class AABB:
    def __init__(self, minCoordinate, maxCoordinate, mass):
        self.minX = minCoordinate[0]
        self.minY = minCoordinate[1]
        self.maxX = maxCoordinate[0]
        self.maxY = maxCoordinate[1]
        if self.minX>self.maxX or self.minY>self.maxY:
            raise MinBiggerThanMaxError

    def moveX(self, acceleration, direction):#right->1, left->-1 등속 직선 운동.
        global FPS,SCREEN_SIZE
        speed = direction*(acceleration)
        self.minX += speed
        self.maxX += speed

        while self.minX<10:
            self.moveX(acceleration,1)
        while self.maxX>SCREEN_SIZE[0]-10:
            self.moveX(acceleration,-1)

class RightTriangle:
    def __init__(self, leftCoordinate, rightCoordinate):
        self.leftX = leftCoordinate[0]
        self.leftY = leftCoordinate[1]
        self.rightX = rightCoordinate[0]
        self.rightY = rightCoordinate[1]
        self.height = abs(self.leftY-self.rightY)
        self.width = self.rightX-self.leftX
        if self.width<0:
            raise Exception("좌표 오류: 왼쪽 x좌표> 오른쪽 x좌표")
        self.flag = False#빗변 기울기가 음수.
        if self.rightY>self.leftY:
            self.flag = True
        
        if self.flag:
            self.AABBForCollision = AABB(leftCoordinate, rightCoordinate, 0)
        else:
            self.AABBForCollision = AABB((self.leftX,self.rightY), (self.rightX, self.leftY), 0)
        

    def moveX(self, acceleration, direction):#right->1, left->-1 등속 직선 운동.
        global FPS,SCREEN_SIZE
        speed = direction*(acceleration)
        self.leftX += speed
        self.rightX += speed

        while self.minX<10:
            self.moveX(acceleration,1)
        while self.maxX>SCREEN_SIZE[0]-10:
            self.moveX(acceleration,-1)

    def isDotUnderHypotenuse(self, dot1):
        x2MinusX1 = self.rightX-self.leftX
        y2MinusY1 = self.rightY-self.leftY
        if (y2MinusY1/x2MinusX1)*(dot1[0]-self.leftX) + self.leftY >dot1[1]:
            return True
        return False

class Triangle:
    def __init__(self, leftCoordinate, middleCoordiante, rightCoordinate):
        self.leftX = leftCoordinate[0]
        self.leftY = leftCoordinate[1]
        self.middleX = middleCoordiante[0]
        self.middleY = middleCoordiante[1]
        self.rightX = rightCoordinate[0]
        self.rightY = rightCoordinate[1]

        if self.leftY != self.rightY or self.middleY <= self.rightY or self.leftX >= self.middleX or self.middleX >= self.rightX:
            raise Exception("좌표 값이 이상합니다. 밑변이 ㅡ와 같은 모양이여야 하고(왼쪽 y == 오른쪽 y), 가운데 y가 가장 커야 하며, (왼쪽, 가운데, 오른쪽)순서로 인수를 입력해야 합니다.")
        
        self.AABBForCollision = AABB((self.leftX, self.rightY), (self.rightX, self.middleY), 0)
        self.leftRightTriangleForCollision = RightTriangle(leftCoordinate, middleCoordiante)
        self.rightRightTriangleForCollision = RightTriangle(middleCoordiante, rightCoordinate)




class Circle:
    def __init__(self, position, radius):
        self.centerX = position[0]
        self.centerY = position[1]
        self.radius = radius
        self.AABBForCollision = AABB( (self.centerX-radius, self.centerY-radius), (self.centerX+radius, self.centerY+radius) ,0)

    def moveX(self, acceleration, direction):#right->1, left->-1 등속 직선 운동.
        global FPS,SCREEN_SIZE
        speed = direction*(acceleration)
        self.centerX += speed

        while self.centerX-self.radius<10:
            self.moveX(acceleration,1)
        while self.centerX+self.radius>SCREEN_SIZE[0]-10:
            self.moveX(acceleration,-1)

class Collision:
    def __init__(self):
        pass
    def getDotvsDotDistance(self,dot1, dot2):
        return(math.sqrt((dot1[0]-dot2[0])**2 + (dot1[1]-dot2[1])**2))
    def getLinevsDotDistance(self, lineDot1, lineDot2, dot1):
        a = lineDot1[0]-lineDot2[0]
        b = lineDot1[1]-lineDot2[1]
        return abs(a*dot1[1] - b*dot1[0] + lineDot2[0]*b - lineDot2[1]*a)/(math.sqrt(a**2 + b**2))#점과 직선사이 공식.
    def LinevsLine(self, line1, line2):#일차방정식으로 넣기.
        pass

    def AABBvsAABB(self, AABB1, AABB2):
        if AABB1.minX>AABB2.maxX or AABB2.minX>AABB1.maxX:
            return False
        elif AABB1.minY>AABB2.maxY or AABB2.minY>AABB1.maxY:
            return False
        else:
            return True
    def CirclevsCircle(self, Circle1, Circle2):
        if self.getDotvsDotDistance((Circle1.centerX, Circle1.centerY), (Circle2.centerX, Circle2.centerY)) < Circle1.radius + Circle2.radius:
            return True
        return False
    def AABBvsCircle(self, AABB1, Circle1):
        if AABB1.maxY<Circle1.centerY-Circle1.radius or AABB1.minY > Circle1.centerY+Circle1.radius:
            return False
        elif AABB1.maxX<Circle1.centerX-Circle1.radius or AABB1.minX>Circle1.centerX+Circle1.radius:
            return False
        else:
            return True
    def AABBvsRightTriangle(self, AABB1, RightTriangle1):
        if self.AABBvsAABB(AABB1, RightTriangle1.AABBForCollision):
            if AABB1.minX<= RightTriangle1.leftX and AABB1.maxX>= RightTriangle1.rightX:
                return True
            if RightTriangle1.flag:
                if RightTriangle1.isDotUnderHypotenuse((AABB1.maxX, AABB1.minY)):
                   return True
            else:
                if RightTriangle1.isDotUnderHypotenuse((AABB1.minX, AABB1.minY)):
                    return True
        return False
    def CirclevsRightTriangle(self, Circle1, RightTriangle1):
        if self.AABBvsAABB(Circle1.AABBForCollision, RightTriangle1.AABBForCollision):
            if self.AABBvsCircle(RightTriangle1.AABBForCollision, Circle1):
                if RightTriangle1.isDotUnderHypotenuse((Circle1.centerX, Circle1.centerY)):
                    return True
                else:
                    if self.getLinevsDotDistance((RightTriangle1.leftX, RightTriangle1.leftY), (RightTriangle1.rightX, RightTriangle1.rightY), (Circle1.centerX, Circle1.centerY)) < Circle1.radius:
                        return True
        return False
    def AABBvsTriangle(self, AABB1, Triangle1):
        if self.AABBvsAABB(AABB1, Triangle1.AABBForCollision):
            if AABB1.minX<= Triangle1.leftX and AABB1.maxX>= Triangle1.rightX:
                return True
            if self.AABBvsRightTriangle(AABB1, Triangle1.leftRightTriangleForCollision):
                return True
            if self.AABBvsRightTriangle(AABB1, Triangle1.rightRightTriangleForCollision):
                return True
            if Triangle1.leftRightTriangleForCollision.isDotUnderHypotenuse(((AABB1.minX + AABB1.maxX)/2, AABB1.minY)):
                return True
            if Triangle1.rightRightTriangleForCollision.isDotUnderHypotenuse(((AABB1.minX + AABB1.maxX)/2, AABB1.minY)):
                return True
        return False
'''
def collisionTestFunc(AABB):
        a = Collision()
        return (a.AABBvsAABB(AABB[0], AABB[1]))
'''






def control(arg, count, id):
    a = Collision()
    m = 0
    for i in range(arg, count):
        if a.AABBvsTriangle(AABB1=AABB((i,i),(2*i+1,3*i+1), 0), Triangle1=Triangle((10, 10), (30,100),(50,10))):
            m+= 1
    print(f"===============id: {id}, 겹치는 사각형,삼각형 개수: {m}=============")


#TEST`
if __name__ == "__main__":
    import time
    import multiprocessing
    from multiprocessing import Process, Manager
    from functools import partial
    from threading import Thread

    multiprocessing.freeze_support()

    FPS = 60 
    SCREEN_SIZE = (1920, 1080)

    a = AABB((4,40), (50,400), 1)
    b = AABB((2,3),(5,6), 1)
    c = Collision()
    print(c.AABBvsAABB(a,b))
    d = Circle((10,500), 40)
    e = Circle((2,4), 8)
    g = Triangle((2,3),(10,6), (15,3))
    print(c.CirclevsCircle(d,e))
    print(c.AABBvsCircle(a,d))
    print(c.AABBvsCircle(a,e))
    print(c.AABBvsCircle(b,d))
    print(c.AABBvsCircle(b,e))
    print(c.AABBvsTriangle(b,g))
    print("======init Finished=========")
    COUNT = 0
    m = 0
    startTime = time.time()
    for i in range(COUNT):
        if c.AABBvsTriangle(AABB1=AABB((i,i),(2*i+1,3*i+1), 0), Triangle1=Triangle((10, 10), (30,100),(50,10))):
            m += 1
    print(f"===========사각형,삼각형 충돌처리 걸린시간: {time.time()-startTime}=========")
    print(f"===========겹치는 사각형, 삼각형 개수: {m}=========================")

    p1 = Process(target=control, args=(0, COUNT//2,1))
    p2 = Process(target=control, args=(COUNT//2, COUNT, 2))
    print("===multiprocessingInit finished====")
    startTime = time.time()
    results = []
    
    p1.start()
    print("=====p1 started======")
    p2.start()
    p1.join()
    print("=====p1 joined======")
    p2.join()
    print(f"===========사각형 충돌처리-multi 걸린시간: {time.time()-startTime}=========")


    '''
    results = []
    m = 0
    startTime = time.time()
    for i in range(COUNT):
        if c.AABBvsAABB(AABB((i,i), (2*i+1, 5*i+1), 0), AABB((10, 100), (500, 600), 0)):
            m+= 1
    print(f"===========사각형 충돌처리-일반 걸린시간: {time.time()-startTime}=========")
    print(f"===========겹치는 사각형 개수: {m}=========================")

    startTime = time.time()
    th1 = Thread(target=control, args=(0, COUNT//2,1))
    th2 = Thread(target=control, args=(COUNT//2, COUNT, 2))
    th1.start()
    th2.start()
    th1.join()
    th2.join()
    procs = []

    for i in range(4):
        proc = Process(target=control, args=(COUNT,1))
        procs.append(proc)
        proc.start()

    for proc in procs:
        proc.join()

    #pool = multiprocessing.Pool(processes=4)
    #argues = [(0, COUNT//4, 1), (COUNT//4, COUNT//2, 2), (COUNT//2, COUNT*3//2, 3), (COUNT*3//2, COUNT, 4)]
    #pool.map(control, argues)
    
    b = []
    startTime = time.time()
    for i in range(COUNT):
        b.append(c.CirclevsCircle(Circle1=Circle((i,i), 5), Circle2=Circle((10, 100), 600)))
    print(f"===========원 충돌처리-multi 걸린시간: {time.time()-startTime}=========")
    m = 0
    for i in range(len(b)):
        if b[i]:
            m += 1
    print(f"===========겹치는 원 개수: {m}=========================")
    '''
    
