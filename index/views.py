# from django.utils import timezone
import random
import time

from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
import socket
from login.models import *
import requests
import re


# Create your views here.


def bookings(request):
    try:
        room = Rooms.objects.filter(is_active=True)

    except Exception as e:
        print(e)

    return render(request, 'index/Bookings.html', {"room": room})


def seat(request, id):
    try:
        room = Rooms.objects.get(id=id)
        rooms = Rooms.objects.filter(is_active=True)
    except Exception as e:
        print(e)
    if request.method == "GET":
        room_selected = request.GET.get('room_id')
        if room_selected:

            time_selected_r = int(request.GET.get('day'))  # 日期
            time_selected_s = int(request.GET.get('time'))  # 时间

            # 日期判断
            d1 = timezone.now()
            time = int(d1.day)
            if time_selected_r == 1:
                time = time
            elif time_selected_r == 2:
                time = time + 1
            # print(time)
            try:
                room_1 = Rooms.objects.get(id=room_selected)
                booking = Bookings.objects.filter(
                    time__day=time,
                    period=time_selected_s,
                    room_id=room_1,
                    is_active=True)

            except Exception as e:
                print(e)
            seat_dict = {}
            for i in range(1, room.number + 1):
                seat_dict[str(i)] = 0
            for i in booking:
                # print("座位号", i.id)
                seat_dict[str(i.number)] = 1

            return render(request, 'index/seat_id.html', {"room": room,
                                                          "rooms": rooms,
                                                          "seat": seat_dict,
                                                          "room_id": room_selected,  # 选择上页自习室一致
                                                          "time_selected_r": time_selected_r,
                                                          "time_selected_s": time_selected_s,
                                                          "room_1": room_1.name,
                                                          })
        else:
            return render(request, 'index/seat.html', {"room": room,
                                                       "rooms": rooms,
                                                       "room_id": room.id})
    elif request.method == 'POST':
        try:
            room_1 = request.POST['room']
            number = request.POST['number']
            period = request.POST['time']
            name = request.session.get('name')
            name = name['name']
            day = request.POST['day']
            print(room, number, period, day, name)
        except:
            return HttpResponseRedirect(request.path_info)
        # 日期判断
        d1 = timezone.now()
        time = int(d1.day)
        if day == 1:
            day = time
        elif day == 2:
            day = time + 1

        # 判断本人有没有已经预约了座位

        try:
            student = Students.objects.get(name=name)
            book = Bookings.objects.filter(
                students_id=student.id,
                time__day=time,
                period=period,
                is_active=True)

        except Exception as e:
            print(e)
        if book:
            msg = "alert"
            return render(request, 'index/seat.html', {"rooms": rooms, "room": room, "room_id": room.id, "msg": msg})
        else:
            try:
                student = Students.objects.get(name=name)
                booking = Bookings.objects.create(
                    students=student,
                    number=int(number),
                    room_id=room_1,
                    period=period

                )
            except Exception as e:
                print(e)
            return HttpResponseRedirect('/index/recording/')


def recording(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    student = request.session.get('name')
    student = student['name']
    id = request.GET.get('id')
    if id:
        try:
            booking = Bookings.objects.get(id=id)
        except Exception as e:
            print(e)
        booking.is_active = False
        booking.save()
        return HttpResponseRedirect("/index/recording/")
    try:
        student = Students.objects.get(name=student).id
        booking = Bookings.objects.filter(students_id=student).order_by('-time')
        # 日期判断
        d1 = timezone.now()
        day = int(d1.day)
        month = int(d1.month)
        return render(request, 'index/Recording.html', {"booking": booking, "day": day, "month": month, "ip": ip})
    except Exception as e:
        print(e)


def warn(request):
    student = request.session.get('name')
    student = student['name']
    try:
        student = Students.objects.get(name=student)
        integrals = Integrals.objects.filter(is_active=True, student_id=student.id)
        return render(request, 'index/warn.html', {"integrals": integrals})
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.path_info)


def sign_url(request):
    if request.method == 'GET':
        student = request.session.get('name')
        student = student['name']
        code = request.GET.get('sign_code', '')

        if code:
            sign = SignCode.objects.all().order_by('-time')
            sign_code = sign[0].text
            if sign_code != code:
                msg = "签到码错误！"
                alert = "alert"
                return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})
            d1 = timezone.now()
            new_period = d1.hour
            if int(new_period) == 10:
                period = 1
            elif int(new_period) == 16:
                period = 2
            elif int(new_period) == 20:
                period = 3
            else:
                msg = "你不在签到时间短内！"
                alert = "alert"
                return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})

            try:

                time = int(d1.day)
                student = Students.objects.get(name=student)
                book = Bookings.objects.filter(
                    students_id=student.id,
                    time__day=time,
                    period=period)

                if book:
                    print('if book')
                    book[0].is_active = 2
                    book[0].save()
                    msg = "签到成功！！"
                    alert = "alert"
                    return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})
                else:
                    msg = "你没有预约！"
                    alert = "alert"
                    return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})

            except Exception as e:
                msg = "你没有预约！"
                alert = "alert"
                return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})

        return render(request, 'index/sign_url.html')
    elif request.method == 'POST':
        return render(request, 'index/sign_url.html')


def sign_code(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]

    code = ''
    for i in range(1, 7):
        code += str(random.randint(0, 9))
    SignCode.objects.create(text=int(code))
    return render(request, 'index/sign_code.html', {'sign_code': int(code), "local_ip": ip})

def auroch(request):
    return render(request, 'index/auroch.html')
