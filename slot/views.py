#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import datetime
import functools
import os
from django.utils import timezone

from django.core.files.storage import default_storage
from django.http import HttpResponseForbidden, HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse, redirect, get_list_or_404
from django.views import View
from django.views.generic import DetailView, DeleteView, ListView, CreateView, UpdateView
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from menu.views import get_user_grant_list
from warehouse.settings import MEDIA_ROOT, EMAIL_IS_SEND
from .models import Warehouse, Haulier, WarehouseProfile, FixWeekday, ProgressRecord, SlotFiles
from users.models import UserProfile, SlotEmailGroup
from utils.email_send import system_sendmail
from utils.tools import exchange_string
from .forms import SlotHaulierForm, SlotHaulierUpdateForm


def user_is_not_staff(func):
    """View decorator that checks a user is allowed to write a review, in negative case the decorator return
    Forbidden """

    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        user_profile = UserProfile.objects.filter(user_id=request.request.user.id)
        if user_profile[0].staff_role == 0:
            return HttpResponseForbidden()

        return func(request, *args, **kwargs)

    return wrapper


def return_record_set(search_date, given_time, hours, minutes, position):
    RecordSet = Warehouse.objects.filter(workdate=search_date,
                                         havetime__exact=given_time,
                                         slottime__hour=hours,
                                         slottime__minute=minutes,
                                         position__position=position,
                                         ).order_by("status")
    return RecordSet


def return_status_record_set(search_date, progress_code, position):
    RecordSet = Warehouse.objects.filter(workdate=search_date,
                                         progress__exact=progress_code,
                                         position__position=position,
                                         )
    return RecordSet


def get_progress_name(progress_code):
    """
    :param progress_code: char 状态的字符
    :return: 状态的名称
    """
    return_name = ""
    if progress_code == '1':
        return_name = str(progress_code) + "-Booked"
    if progress_code == '2':
        return_name = str(progress_code) + "-Arrived"
    if progress_code == '3':
        return_name = str(progress_code) + "-Loading"
    if progress_code == '4':
        return_name = str(progress_code) + "-Finished"
    if progress_code == '5':
        return_name = str(progress_code) + "-Abnormal"

    return return_name


def reset_time_00_or_40(need_time):
    this_hour = int(need_time[0:2])
    this_min = int(need_time[3:5])
    if this_hour == 6 and this_min < 40:
        this_hour = '06'
        this_min = '00'

    if (this_hour == 6 and this_min >= 40) or (this_hour == 7 and this_min < 20):
        this_hour = '06'
        this_min = '40'

    if this_hour == 7 and 20 <= this_min <= 59:
        this_hour = '07'
        this_min = '20'

    if this_hour == 8 and this_min < 40:
        this_hour = '08'
        this_min = '00'

    if (this_hour == 8 and this_min >= 40) or (this_hour == 9 and this_min < 20):
        this_hour = '08'
        this_min = '40'

    if this_hour == 9 and 20 <= this_min <= 59:
        this_hour = '09'
        this_min = '20'

    if this_hour == 10 and this_min < 40:
        this_hour = '10'
        this_min = '00'

    if (this_hour == 10 and this_min >= 40) or (this_hour == 11 and this_min < 20):
        this_hour = '10'
        this_min = '40'

    if this_hour == 11 and 20 <= this_min <= 59:
        this_hour = '11'
        this_min = '20'

    if this_hour == 12 and this_min < 40:
        this_hour = '12'
        this_min = '00'

    if (this_hour == 12 and this_min >= 40) or (this_hour == 13 and this_min < 20):
        this_hour = '12'
        this_min = '40'

    if this_hour == 13 and 20 <= this_min <= 59:
        this_hour = '13'
        this_min = '20'

    if this_hour == 14 and this_min < 40:
        this_hour = '14'
        this_min = '00'

    if (this_hour == 14 and this_min >= 40) or (this_hour == 15 and this_min < 20):
        this_hour = '14'
        this_min = '40'

    if this_hour == 15 and this_min < 30:
        this_hour = '15'
        this_min = '20'

    new_time = this_hour + ":" + this_min
    return new_time


def reset_time_00_or_30(need_time):
    this_hour = need_time[0:2]
    this_min = need_time[3:5]
    if this_hour != '30' and this_min != '00':
        if this_min > '30':
            this_hour = int(this_hour) + 1
            if this_hour < 10:
                this_hour = '0' + str(this_hour)
            this_min = '00'
        else:
            this_min = '30'
    new_time = this_hour + ":" + this_min
    return new_time


# 获取所有 确定时间的 slot 的列表
def get_all_slot(search_date, position):
    all_slots = []
    warehouse_profile = WarehouseProfile.objects.filter(position__exact=position)
    if warehouse_profile:
        point = []
        work_begin_time = warehouse_profile[0].beginworktime
        time_gap = warehouse_profile[0].time_gap
        end_time = warehouse_profile[0].overworktime
        this_time = work_begin_time.strftime('%H:%M')
        end_time = end_time.strftime('%H:%M')
        while end_time >= this_time:
            point.append(this_time)
            work_datetime = datetime.datetime.strptime(this_time, '%H:%M')
            this_time = (work_datetime + datetime.timedelta(minutes=time_gap)).strftime('%H:%M')

        for time_string in point:
            # return_record_set(search_date, given_time, hours, minutes, position):
            hours = int(time_string[0:2])
            minutes = int(time_string[3:5])
            all_slots.append([time_string, return_record_set(search_date, 1, hours, minutes, position)])

    return all_slots


def slot_time_return_parameter(request, search_date, post_context={}):
    # ======================================================
    # slot list 需要返回的参数
    # ======================================================
    # 通过登录的用户，查找到当前操作仓库的最大 Max_slot
    position = request.user.profile.op_position
    location_result = UserProfile.objects.filter(user_id=request.user.id, )
    if location_result:
        position = location_result[0].op_position

    location_result = WarehouseProfile.objects.filter(position=position)
    max_slot_number = 0
    if location_result:
        max_slot_number = location_result[0].maxslot

    # 获取所有确定时间的 slot
    all_slots = get_all_slot(search_date, position)

    # 没有确定时间的INBOUND
    all_NoInSlotsTimes = Warehouse.objects.filter(workdate=search_date,
                                                  havetime__exact=0,
                                                  status__exact="INBOUND",
                                                  position__position=position,
                                                  ).order_by("hailerid")
    all_NoInSlotsCount = 0
    if all_NoInSlotsTimes:
        all_NoInSlotsCount = len(all_NoInSlotsTimes)

    # 没有确定时间的OUTBOUND
    all_NoOutSlotsTimes = Warehouse.objects.filter(workdate=search_date,
                                                   havetime__exact=0,
                                                   status__exact="OUTBOUND",
                                                   position__position=position,
                                                   ).order_by("hailerid")
    all_NoOutSlotsCount = 0
    if all_NoOutSlotsTimes:
        all_NoOutSlotsCount = len(all_NoOutSlotsTimes)

    all_NoSlotsTimes = all_NoInSlotsCount + all_NoOutSlotsCount
    # 取得所有车辆的状态情况
    all_progress_booked = return_status_record_set(search_date, 1, position)
    all_progress_arrived = return_status_record_set(search_date, 2, position)
    all_progress_loading = return_status_record_set(search_date, 3, position)
    all_progress_finished = return_status_record_set(search_date, 4, position)
    all_progress_abnormal = return_status_record_set(search_date, 5, position)

    # 取得Haulier的数据
    all_hauliers = Haulier.objects.filter(position__position=position)
    parameter = {"searching_date": search_date,
                 "all_slots": all_slots,
                 "all_NoInSlotsTimes": all_NoInSlotsTimes,
                 "all_NoOutSlotsTimes": all_NoOutSlotsTimes,
                 "all_NoSlotsTimes": all_NoSlotsTimes,
                 "all_hauliers": all_hauliers,
                 "max_slot_number": max_slot_number,
                 "all_progress_booked": all_progress_booked,
                 "all_progress_arrived": all_progress_arrived,
                 "all_progress_loading": all_progress_loading,
                 "all_progress_finished": all_progress_finished,
                 "all_progress_abnormal": all_progress_abnormal,
                 "page_tab": 1,
                 'menu_grant': get_user_grant_list(request.user.id, "BOOKING-SYSTEM"),
                 }
    parameter = dict(parameter, **post_context)
    return parameter


class SlotListView(View):
    @user_is_not_staff
    def get(self, request):
        search_date = request.GET.get("searching_date", datetime.date.today())

        parameter = slot_time_return_parameter(request, search_date)
        return render(request, "SlotList.html", parameter)

    @user_is_not_staff
    def post(self, request):
        haulier = request.POST.get("haulier", 0)  # 承运人
        delivery_ref = request.POST.get("delivery_ref", "")
        work_date = request.POST.get("work_date", datetime.datetime.now())  # 抵达日期
        vehicle_reg = request.POST.get("vehicle_reg", 0)  # 车牌号码
        status = request.POST.get("status", 0)  # INBOUND OR OUTBOUND
        given_time = request.POST.get("given_time", '1')  # 是否给出确定时间， 0 未确定slot时间
        slot_time = request.POST.get("slot_time", "00:00")  # 承运时间
        haulier_result = Haulier.objects.filter(code__exact=haulier, )
        haulier_id = 0
        if haulier_result:
            haulier_id = haulier_result[0].id  # 承运人id
        # 根据用户能够操作的地点， 判断仓库的位置
        position = request.user.profile.op_position  # 仓库位置

        tmp_delivery_ref = haulier + delivery_ref
        filter_result = Warehouse.objects.filter(deliveryref__exact=tmp_delivery_ref)
        strError = ""
        if filter_result:
            strError = ["delivery_ref", "This Delivery Ref. is Existed"]
        else:
            if given_time == "1":
                yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
                d_work_date = datetime.datetime.strptime(work_date, "%Y-%m-%d")

                if d_work_date < yesterday:
                    strError = ["work_date", "You can not select the date before today. "]
                else:
                    # 不能更新成为当前日期之后10天的日期
                    last_day = 10
                    diff_day = (d_work_date - yesterday).days
                    if diff_day >= last_day:
                        strError = ["work_date", "Only input date within 10 days."]
                    else:
                        # 判断时间，并转换成为整点 00 或 30
                        time_result = WarehouseProfile.objects.filter(position__exact=position)
                        begin_time = datetime.time(0).strftime("%H:%M")
                        over_time = datetime.time(0).strftime("%H:%M")
                        if time_result:
                            begin_time = time_result[0].beginworktime.strftime("%H:%M")
                            over_time = time_result[0].overworktime.strftime("%H:%M")

                        if slot_time < begin_time or slot_time > over_time:
                            if slot_time == "":
                                strError = ["slot_time", "Error: Slot Time is Empty."]
                            else:
                                strError = ["slot_time", slot_time + " - Slot Time is NOT work time."]
                        else:
                            time_gap = WarehouseProfile.objects.filter(position__exact=position)
                            if time_gap[0].time_gap == 30:
                                slot_time = reset_time_00_or_30(slot_time)
                            else:
                                slot_time = reset_time_00_or_40(slot_time)
                            slot_hour = slot_time[0:2]
                            slot_min = slot_time[3:5]

                            # 需要在此判断， 该时间段是否已经满了？
                            if position == request.user.profile.op_position and given_time == 1:
                                warehouse_profile_result = WarehouseProfile.objects.filter(position=position)
                                max_count = 0
                                max_inbound_count = 0
                                if warehouse_profile_result:
                                    max_count = warehouse_profile_result[0].maxslot
                                    max_inbound_count = warehouse_profile_result[0].maxinbound

                                # 检查是否有预留的公司时间
                                weekday = datetime.datetime.strptime(work_date, '%Y-%m-%d').weekday() + 1
                                check_date_result = FixWeekday.objects.filter(weekday=weekday,
                                                                              time__hour=slot_hour,
                                                                              time__minute=slot_min,
                                                                              status=1)
                                count_preserves = 0
                                if check_date_result:
                                    count_preserves = check_date_result.count()

                                # 检查该时间段， 有多少台车已经booking
                                warehouse_result = Warehouse.objects.filter(workdate=work_date,
                                                                            slottime__hour=slot_hour,
                                                                            slottime__minute=slot_min,
                                                                            havetime__exact=1,
                                                                            position__position=position,
                                                                            )
                                count_orders = 0
                                if warehouse_result:
                                    count_orders = warehouse_result.count()

                                if count_orders + count_preserves >= max_count:
                                    strError = ["slot_time", "Over max handle number. "]
                                else:
                                    if status == "INBOUND":
                                        # 检查该时间段， 最大的INBOUND的数量是否已经爆满
                                        warehouse_result = Warehouse.objects.filter(workdate=work_date,
                                                                                    slottime__hour=slot_hour,
                                                                                    slottime__minute=slot_min,
                                                                                    havetime__exact=1,
                                                                                    status="INBOUND",
                                                                                    position__position=position,
                                                                                    )
                                        count_inbound_order = warehouse_result.count()
                                        if count_inbound_order >= max_inbound_count:
                                            strError = ["slot_time", "Inbound number is full. "]
            else:
                slot_time = "06:00"
        if strError:
            context = {"haulier_id": haulier_id,
                       "delivery_ref": delivery_ref,
                       "work_date": work_date,
                       "vehicle_reg": vehicle_reg,
                       "status": status,
                       "given_time": given_time,
                       "slot_time": slot_time,
                       "searching_date": work_date,
                       "ErrorMsg": strError,
                       }
            parameter = slot_time_return_parameter(request, work_date, context)

            return render(request, "SlotList.html", parameter)
        else:
            new_ref = haulier + delivery_ref.upper()
            warehouse = Warehouse()
            warehouse.deliveryref = new_ref
            warehouse.workdate = work_date
            warehouse.slottime = slot_time
            warehouse.vehiclereg = vehicle_reg.upper()
            warehouse.status = status.upper()
            warehouse.progress = 1  # 1=Booked 2=Arrived 3=Loading 4=Finished 5=abnormal
            warehouse.havetime = given_time
            warehouse.hailerid_id = haulier_id
            warehouse.position_id = position
            warehouse.op_user_id = request.user.id
            warehouse.op_datetime = timezone.now()
            warehouse.save()

            progressRecord = ProgressRecord()
            progressRecord.deliveryref = haulier + delivery_ref.upper()
            progressRecord.progress = 1  # 1=Booked 2=Arrived 3=Loading 4=Finished 5=abnormal
            progressRecord.position = position
            progressRecord.op_user_id = request.user.id
            progressRecord.progress_name = "1-Booked"
            progressRecord.remark = "Create Booked"
            progressRecord.save()

            parameter = slot_time_return_parameter(request, work_date, )

            return render(request, "SlotList.html", parameter)


class SlotDetailView(DetailView):
    # queryset = Warehouse.objects.all()
    model = Warehouse
    template_name = "Slot_Detail.html"

    def get_context_data(self, **kwargs):
        context = super(SlotDetailView, self).get_context_data(**kwargs)
        context['files'] = SlotFiles.objects.filter(delivery_ref=self.object).order_by(
            'is_void',
            'order',
            'files_profile',
            'file_name',
            'uploaded_at',
        )
        context['page_tab'] = int(self.kwargs['slug'])
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")
        return context

    @user_is_not_staff
    def get_object(self):
        # get_object() 默认时返回通过 pk 或 slug 筛选出的对象（该视图需要操作的对象）
        # Call the superclass
        object = super().get_object()
        return object


class SlotUpdateView(View):
    @user_is_not_staff
    def post(self, request):
        new_work_date = request.POST.get("new_work_date", 0)  # 新抵达日期
        is_update_progress = False  # 变更状态初始值为假
        delivery_ref = request.POST.get("delivery_ref", "can_not_be_post")
        page_tab = request.POST.get("page_tab", 1)
        slot_result = Warehouse.objects.filter(deliveryref=delivery_ref)
        if slot_result:
            pk = slot_result[0].id
            new_time = request.POST.get("new_slot_time", 0)  # 新旧抵达时间
            old_work_date = slot_result[0].workdate
            old_time = slot_result[0].slottime
            old_given_time = slot_result[0].havetime
            status = slot_result[0].status
            old_progress = str(slot_result[0].progress)
            old_remark = slot_result[0].remark.strip()
            new_remark = request.POST.get("new_remark", "").strip()  # 新备注
            remark_reason = ""  # 记录修改的原因
            progress_name = get_progress_name(old_progress)
            new_progress = old_progress
            progress = old_progress

            if request.user.profile.staff_role != 1:  # 只有仓库人员或经理才能更新状态
                if new_work_date == 0:  # 仓库人员进入后，日期读数将为0， 重置新日期及时间
                    new_work_date = datetime.datetime.strftime(old_work_date, "%Y-%m-%d")
                    new_time = old_time.strftime("%H:%M")
                new_progress = request.POST.get("new_progress", 0)  # 新状态
                if new_progress != old_progress:
                    old_progress_name = progress_name
                    progress = new_progress
                    progress_name = get_progress_name(new_progress)
                    remark_reason = " | Modify Status: From " + old_progress_name + " To " + progress_name  # 记录修改状态
                    is_update_progress = True
                    # 判断进程的顺序， 如果顺序不对，则返回失败信息
                    if new_progress != '5' and old_progress != '5':
                        if new_progress < old_progress:  # 返回保存错误
                            error_string = "You can not change the progress from " + old_progress_name + \
                                           " To " + progress_name + ". "
                            return render(request, "Slot_Save_Error.html", {'ErrorMsg': error_string,
                                                                            "page_tab": 1,
                                                                            'menu_grant': get_user_grant_list(
                                                                                request.user.id, "BOOKING-SYSTEM"),
                                                                            })

            havetime = request.POST.get("new_haveTime", 1)  # 是否确定时间， 0 未确定， 1 确定

            if old_given_time != havetime:
                remark_reason = remark_reason + " | Modify Have Time: From " + str(old_given_time) \
                                + " To " + str(havetime)  # 记录修改是否确定时间

            if havetime == 1:  # 有确定的时间，才去判断仓库是否能够接受
                compare_old_date = datetime.datetime.strftime(old_work_date, "%Y-%m-%d")
                compare_old_time = old_time.strftime("%H:%M")[0:5]

                if not (new_work_date == compare_old_date and new_time == compare_old_time):
                    remark_reason = remark_reason + " | Modify DateTime: From " + compare_old_date + \
                                    " " + compare_old_time + " To " + new_work_date + " " + new_time  # 记录修改时间
                    position = request.user.profile.op_position  # 仓库位置
                    yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
                    d_work_date = datetime.datetime.strptime(new_work_date, "%Y-%m-%d")
                    # 不能更新成为当前日期之前的日期
                    if d_work_date < yesterday:
                        error_string = "You can not change to be " + d_work_date.strftime("%Y-%m-%d") + \
                                       " because select the date before today. "
                        return render(request, "Slot_Save_Error.html", {'ErrorMsg': error_string,
                                                                        "page_tab": 1,
                                                                        'menu_grant': get_user_grant_list(
                                                                            request.user.id, "BOOKING-SYSTEM"),
                                                                        })

                    # 不能更新成为当前日期之后10天的日期
                    last_day = 10
                    diff_day = (d_work_date - yesterday).days
                    if diff_day >= last_day:
                        error_string = " You cannot set the date more than 10 days after the current date"
                        return render(request, "Slot_Save_Error.html", {'ErrorMsg': error_string,
                                                                        "page_tab": 1,
                                                                        'menu_grant': get_user_grant_list(
                                                                            request.user.id, "BOOKING-SYSTEM"),
                                                                        })

                    # 判断时间，并转换成为整点 00 或 30
                    time_result = WarehouseProfile.objects.filter(position__exact=position)
                    begin_time = datetime.time(0).strftime("%H:%M")
                    over_time = datetime.time(0).strftime("%H:%M")
                    if time_result:
                        begin_time = time_result[0].beginworktime.strftime("%H:%M")
                        over_time = time_result[0].overworktime.strftime("%H:%M")

                    if new_time < begin_time or new_time > over_time:
                        error_string = "We are opening time is " + begin_time + " to  " + over_time + \
                                       ", Please check your input time ( " + new_time + ")"
                        return render(request, "Slot_Save_Error.html", {'ErrorMsg': error_string,
                                                                        "page_tab": 1,
                                                                        'menu_grant': get_user_grant_list(
                                                                            request.user.id, "BOOKING-SYSTEM"),
                                                                        })
                    time_gap = WarehouseProfile.objects.filter(position__exact=position)
                    if time_gap[0].time_gap == 30:
                        new_time = reset_time_00_or_30(new_time)
                    else:
                        new_time = reset_time_00_or_40(new_time)

                    slot_hour = new_time[0:2]
                    slot_min = new_time[3:5]

                    # 需要在此判断， 该时间段是否已经满了？
                    if new_progress == old_progress:  # 如果是修改状态，则不必要判断是否满了
                        if position == request.user.profile.op_position and havetime == 1:
                            warehouse_profile_result = WarehouseProfile.objects.filter(position=position)
                            max_count = 0
                            max_inbound_count = 0
                            if warehouse_profile_result:
                                max_count = warehouse_profile_result[0].maxslot
                                max_inbound_count = warehouse_profile_result[0].maxinbound

                            # 检查是否有预留的公司时间
                            weekday = datetime.datetime.strptime(new_work_date, '%Y-%m-%d').weekday() + 1
                            check_date_result = FixWeekday.objects.filter(weekday=weekday,
                                                                          time__hour=slot_hour,
                                                                          time__minute=slot_min,
                                                                          status=1)
                            count_preserves = 0
                            if check_date_result:
                                count_preserves = check_date_result.count()

                            # 检查该时间段， 有多少台车已经booking
                            warehouse_result = Warehouse.objects.filter(workdate=new_work_date,
                                                                        slottime__hour=slot_hour,
                                                                        slottime__minute=slot_min,
                                                                        havetime__exact=1)
                            count_orders = 0
                            if warehouse_result:
                                count_orders = warehouse_result.count()

                            if count_orders + count_preserves >= max_count:
                                error_string = "Max handle number is " + str(max_count) + \
                                               ". But System already have booking number is " + \
                                               str(count_orders) + " and Preserves number is " + str(count_preserves)
                                return render(request, "Slot_Save_Error.html", {'ErrorMsg': error_string,
                                                                                "page_tab": 1,
                                                                                'menu_grant': get_user_grant_list(
                                                                                    request.user.id, "BOOKING-SYSTEM"),
                                                                                })

                            if status == "INBOUND":
                                # 检查该时间段， 最大的INBOUND的数量是否已经爆满
                                warehouse_result = Warehouse.objects.filter(workdate=new_work_date,
                                                                            slottime__hour=slot_hour,
                                                                            slottime__minute=slot_min,
                                                                            havetime__exact=1,
                                                                            status="INBOUND")
                                count_inbound_order = warehouse_result.count()
                                if count_inbound_order >= max_inbound_count:
                                    error_string = "INBOUND NUMBER IS FULL, Because We only can " \
                                                   "handle Max Inbound number is " \
                                                   + str(max_inbound_count)
                                    return render(request, "Slot_Save_Error.html", {'ErrorMsg': error_string,
                                                                                    "page_tab": 1,
                                                                                    'menu_grant': get_user_grant_list(
                                                                                        request.user.id, "BOOKING-SYSTEM"),
                                                                                    })

            if old_remark != new_remark:
                remark_reason = remark_reason + " | Modify Remark: From " + old_remark \
                                + " To " + new_remark  # 记录修改备注

            if remark_reason != "":
                warehouse = Warehouse.objects.get(deliveryref=delivery_ref)
                warehouse.workdate = new_work_date
                warehouse.slottime = new_time
                warehouse.havetime = havetime
                warehouse.progress = int(progress)  # 1=Booked 2=Arrived 3=Loading 4=Finished 5=Abnormal
                warehouse.remark = new_remark
                warehouse.save()

                progressRecord = ProgressRecord()
                progressRecord.deliveryref = delivery_ref
                progressRecord.progress = progress
                progressRecord.position = request.user.profile.op_position
                progressRecord.op_user_id = request.user.id
                progressRecord.progress_name = progress_name
                progressRecord.remark = remark_reason
                progressRecord.save()

                if EMAIL_IS_SEND and is_update_progress:
                    # 状态变更为 arrived 或 finished, 需要发邮件提醒原操作员
                    op_id = slot_result[0].op_user_id
                    user_queryset = User.objects.filter(id=op_id)
                    op_name = user_queryset[0].username
                    file_list = []
                    email_to_list = [user_queryset[0].email]
                    position = request.user.profile.op_position
                    if progress == '2':  # 2 - Arrived
                        system_sendmail(delivery_ref, op_name, file_list, email_to_list, 'Arrived', position, )
                    elif progress == '4':  # 4 - Finished
                        system_sendmail(delivery_ref, op_name, file_list, email_to_list, 'Finished', position, )

            return redirect('slot:slot_detail', pk=pk, slug=page_tab)


class SlotTimeDeleteView(DeleteView):
    model = Warehouse
    template_name = "Slot_Confirm_Delete.html"

    @user_is_not_staff
    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(SlotTimeDeleteView, self).get_object()
        return obj

    def get_context_data(self, **kwargs):
        context = super(SlotTimeDeleteView, self).get_context_data(**kwargs)
        context['page_tab'] = 1
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")
        return context

    @user_is_not_staff
    def get_success_url(self):
        return reverse('slot:slot_list')


class SlotSearchListView(ListView):
    model = Warehouse
    template_name = 'slot_search_list.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_delivery = self.request.GET.get('s_delivery', '')
        query_progress = self.request.GET.get('progress', '0')
        query_haulier = int(self.request.GET.get('s_haulier', '0'))

        context['all_haulier'] = Haulier.objects.filter(position__position=self.request.user.profile.op_position)
        context['query_delivery'] = query_delivery
        context['query_progress'] = query_progress
        context['query_haulier'] = query_haulier

        context['page_tab'] = 2
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")

        return context

    def get_queryset(self):
        query_delivery = self.request.GET.get('s_delivery', '')
        query_progress = self.request.GET.get('progress', '0')
        query_haulier = self.request.GET.get('s_haulier', '0')

        date_filter = self.request.GET.get('range_date_filter', '')

        query = Q(position__position=self.request.user.profile.op_position)
        query_ref = Q(deliveryref__icontains=query_delivery)
        if date_filter:
            begin_date = datetime.datetime.strptime(date_filter[0:10], '%Y/%m/%d')
            end_date = datetime.datetime.strptime(date_filter[13:23], '%Y/%m/%d')
            query = Q(query, workdate__range=(begin_date, end_date))

        if query_haulier != '0' and query_progress != '0':  # 条件均有
            haulier_condition = Q(progress__exact=query_progress)
            progress_condition = Q(hailerid__id=query_haulier)
            result_list = Warehouse.objects.filter(query_ref & query & haulier_condition & progress_condition)\
                .order_by('-workdate', 'slottime')
        elif query_haulier != '0' and query_progress == '0':  # 只是查询 Haulier.
            haulier_condition = Q(hailerid__id=query_haulier)
            result_list = Warehouse.objects.filter(haulier_condition & query & query_ref).order_by('-workdate',
                                                                                                   'slottime')
        elif query_haulier == '0' and query_progress != '0':  # 只是查询 Progress.
            progress_condition = Q(progress__contains=query_progress)
            result_list = Warehouse.objects.filter(progress_condition & query & query_ref).order_by('-workdate',
                                                                                                    'slottime')
        else:
            result_list = Warehouse.objects.filter(query & query_ref).order_by('-workdate', 'slottime')

        return result_list


# https://simpleisbetterthancomplex.com/tutorial/2016/11/22/django-multiple-file-upload-using-ajax.html
# https://github.com/Julyaan/dragToUpload/blob/master/upload.html
# https://www.jianshu.com/p/0b9bdbfde29a
# https://blog.csdn.net/tangran0526/article/details/104156857
# https://www.pianshen.com/article/583491278/
# https://www.pythonf.cn/read/91823
# https://zhuanlan.zhihu.com/p/47287495  Django文件上传需要考虑的重要事项


def get_new_file_name(file_name, ref, send_type):
    # file_name = re.findall(r'(.+?)\.', file_name) //去掉扩展名后的文件名
    ext = file_name.split('.')[-1].upper()
    if send_type == 'OP Form':
        # 根据本地文件名，判断是否有重名，如果有，则自动增加版本号
        all_file = SlotFiles.objects.filter(delivery_ref__deliveryref__exact=ref, local_file_name__exact=file_name,
                                            files_profile__exact=send_type)
        if all_file:
            if (all_file.count() + 1) < 10:
                version = '-V0' + str(all_file.count() + 1)
            else:
                version = 'V' + str(all_file.count() + 1)
            file_name = file_name + version
        else:
            file_name = file_name + '-V01'
    else:
        all_file = SlotFiles.objects.filter(delivery_ref__deliveryref__exact=ref, files_profile__exact=send_type)
        if all_file:
            if (all_file.count() + 1) < 10:
                version = '-V0' + str(all_file.count() + 1)
            else:
                version = 'V' + str(all_file.count() + 1)
            file_name = ref + version
        else:
            file_name = ref + '-V01'
    file_name = exchange_string(file_name) + '.' + ext
    return file_name


@csrf_exempt
def uploads(request):
    if request.is_ajax():
        if request.method == "POST":
            ref = request.POST['ref_no']  # 获取前台传入的 delivery ref send_type
            send_type = request.POST['send_type']  # 获取前台传入的 send_type
            warehouse_queryset = get_list_or_404(Warehouse.objects.filter(deliveryref=ref))
            ref_id = warehouse_queryset[0].id
            op_name = request.user.username
            email_to_list = [request.user.email, ]
            file_list = []
            is_send_mail = False
            for local_file_name in request.FILES:  # 遍历获取request请求中的文件名
                file_name = get_new_file_name(local_file_name, ref, send_type)
                upload_file_path = os.path.join('slot_files', file_name)  # 此目录为文件上传后的服务器目录及文件名
                # 目前，此段新建目录总是失败，需要检查原因
                # absolute_file_path = os.path.join('media', upload_file_path,)
                # #
                # directory = os.path.dirname(absolute_file_path)
                # print('absolute_file_path = ' + absolute_file_path)
                # if not os.path.exists(directory):   # 文件夹不存在，则创建新的文件夹，目前不成功
                #     print('make dir')
                #     os.makedirs(directory, mode=0o777)
                # print('directory = ' + directory)
                # file_name = '{}.{}'.format(uuid.uuid4().hex[:10], ext)  随机文件名
                # file path relative to 'media' folder

                file_data = request.FILES.get(local_file_name)  # 将在内存中本地文件内容读入data中

                with default_storage.open(upload_file_path, mode="wb") as new_file:  # 写入文件到服务器
                    for chunk in file_data.chunks():  # 将文件内容写入到文件中去
                        new_file.write(chunk)
                    new_file.close()

                # 将数据保存到数据库中
                if send_type == 'OP Form':
                    conditions_dic = {
                        'delivery_ref__deliveryref__exact': ref,
                        'local_file_name__exact': local_file_name,
                        'files_profile__exact': send_type,
                        'is_void': 0
                    }
                else:
                    # 将现有的文件有效的作废
                    conditions_dic = {
                        'delivery_ref__deliveryref__exact': ref,
                        'files_profile__exact': send_type,
                        'is_void': 0
                    }
                old_file = SlotFiles.objects.filter(**conditions_dic)
                if old_file:
                    old_file = SlotFiles.objects.get(**conditions_dic)
                    old_file.is_void = 1
                    old_file.save()

                # send_type
                # 操作员：Inbound :  Delivery Manifest
                #                   OP Form
                #        Outbound: Delivery Note
                # 仓库： 状态变更：   Arrived
                #                   Finished
                #       上传文件：Inbound: Breakdown
                #                         Parcel List
                #                         Delivery POD
                #
                #                Outbound: Paperwork

                if send_type == 'Delivery Manifest':
                    order_by = 1
                elif send_type == 'Breakdown':
                    order_by = 2
                elif send_type == 'Parcel List':
                    order_by = 2
                elif send_type == 'Delivery POD':
                    order_by = 2
                elif send_type == 'OP Form':
                    order_by = 5
                elif send_type == 'Delivery Note':
                    order_by = 1
                elif send_type == 'Paperwork':
                    order_by = 4

                # 保存新的文件记录
                slot_files = SlotFiles()
                slot_files.delivery_ref_id = ref_id
                slot_files.file_name = file_name
                slot_files.files_profile = send_type
                slot_files.local_file_name = local_file_name
                slot_files.is_void = 0
                slot_files.order = order_by
                slot_files.op_user_id = request.user.id
                slot_files.save()
                file_list.append(file_name)
                is_send_mail = True

            # 发送邮件
            if EMAIL_IS_SEND and is_send_mail:
                position = request.user.profile.op_position
                system_sendmail(ref, op_name, file_list, email_to_list, send_type, position)

            return redirect('slot:slot_detail', pk=ref_id)
    return HttpResponse('Failure!')


def file_iterator(file_name, chunk_size=512):
    with open(file_name, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


def file_download(request):
    if request.method == 'GET':
        file_original_name = request.GET['filename']
        file_path_name = os.path.join(MEDIA_ROOT, file_original_name)
        if not os.path.exists(file_path_name):
            raise IOError('file not found')

        # response = StreamingHttpResponse(open(file_path_name, 'rb'))
        response = StreamingHttpResponse(file_iterator(file_path_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename=' + file_original_name
        return response
        # print FilePath
    else:
        return HttpResponse('method must be GET')


# SLOT 系统的用户列表
class SlotUserListView(ListView):
    ordering = ["email"]
    model = UserProfile
    template_name = 'slot_users_list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        email_group_queryset = SlotEmailGroup.objects.filter(
            position__exact=self.request.user.profile.op_position,
        )
        context['all_email_group'] = email_group_queryset
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")
        context['page_tab'] = 3
        return context

    def get_queryset(self):
        query_username = self.request.GET.get('username', '')
        query_email = self.request.GET.get('email', '')
        role = int(self.request.GET.get('role', '99'))
        status = int(self.request.GET.get('status', '99'))
        user_queryset = UserProfile.objects.filter(user_id__exact=self.request.user.id, )
        if status == 99 and role == 99:
            result = UserProfile.objects.filter(user__email__icontains=query_email,
                                                user__username__icontains=query_username,
                                                system_menu="BOOKING-SYSTEM",
                                                op_position__exact=self.request.user.profile.op_position,
                                                )

        elif status == 99 and role != 99:
            result = UserProfile.objects.filter(user__email__icontains=query_email,
                                                user__username__icontains=query_username,
                                                staff_role=role,
                                                system_menu="BOOKING-SYSTEM",
                                                op_position__exact=self.request.user.profile.op_position,
                                                )

        elif status != 99 and role == 99:
            result = UserProfile.objects.filter(user__email__icontains=query_email,
                                                user__username__icontains=query_username,
                                                user__is_active=status,
                                                system_menu="BOOKING-SYSTEM",
                                                op_position__exact=self.request.user.profile.op_position,
                                                )
        else:
            result = UserProfile.objects.filter(user__email__icontains=query_email,
                                                user__username__icontains=query_username,
                                                user__is_active=status,
                                                staff_role=role,
                                                system_menu="BOOKING-SYSTEM",
                                                op_position__exact=self.request.user.profile.op_position,
                                                )
        result = user_queryset.union(result)
        return result


class SlotHaulierListView(ListView):
    model = Haulier
    template_name = 'slot_haulier_list.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_tab'] = 4
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")

        return context

    def get_queryset(self):
        query_code = self.request.GET.get('code', '')
        query_name = self.request.GET.get('name', '')
        query_status = self.request.GET.get('status', '99')

        query = Q(position__position=self.request.user.profile.op_position)
        if query_status != '99':
            query1 = Q(code__icontains=query_code)
            query2 = Q(name__icontains=query_name)
            query3 = Q(is_use=query_status)
            result_list = Haulier.objects.filter(query1 & query2 & query3 & query).order_by('code')
        else:
            result_list = Haulier.objects.filter(query, ).order_by('code')

        return result_list


class SlotHaulierCreateView(CreateView):
    model = Haulier
    form_class = SlotHaulierForm
    template_name = 'slot_add_haulier.html'
    success_url = '/slot/haulier-list/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.op_user_id = self.request.user.id
        self.object.op_datetime = datetime.datetime.now()
        self.object.position_id = self.request.user.profile.op_position
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        pass

    def get_initial(self, *args, **kwargs):
        initial = super(SlotHaulierCreateView, self).get_initial(**kwargs)
        initial["position"] = self.request.user.profile.op_position
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_tab'] = 4
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")

        return context


class SlotHaulierUpdateView(UpdateView):
    model = Haulier
    form_class = SlotHaulierUpdateForm
    template_name = 'slot_edit_haulier.html'
    success_url = '/slot/haulier-list/'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.op_user_id = self.request.user.id
        self.object.op_datetime = datetime.datetime.now()
        self.object.position_id = self.request.user.profile.op_position
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        pass

    def get_initial(self, *args, **kwargs):
        initial = super(SlotHaulierUpdateView, self).get_initial(**kwargs)
        initial["position"] = self.request.user.profile.op_position
        return initial

    # def get_form_kwargs(self, *args, **kwargs):
    #     kwargs = super(SlotHaulierUpdateView, self).get_form_kwargs(*args, **kwargs)
    #     kwargs['user'] = self.request.user
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_tab'] = 4
        context['menu_grant'] = get_user_grant_list(self.request.user.id, "BOOKING-SYSTEM")

        return context
