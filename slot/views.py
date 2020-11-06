#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import datetime
import functools
import os
from django.utils import timezone

from django.core.files.storage import default_storage
from django.http import HttpResponseForbidden, HttpResponse, StreamingHttpResponse
from django.shortcuts import render, reverse, redirect, get_list_or_404
from django.views import View
from django.views.generic import DetailView, DeleteView, ListView
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User

from warehouse.settings import MEDIA_ROOT, EMAIL_FROM, EMAIL_IS_SEND
from .forms import SlotTimeForm, SlotTimeUpdateForm
from .models import Warehouse, Haulier, WarehouseProfile, FixWeekday, ProgressRecord, SlotFiles
from users.models import UserProfile
from utils.email_send import system_sendmail
from utils.tools import exchange_string


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


def return_record_set(search_date, havetime, hours, minutes):
    RecordSet = Warehouse.objects.filter(workdate=search_date,
                                         havetime__exact=havetime,
                                         slottime__hour=hours,
                                         slottime__minute=minutes,
                                         ).order_by("status")
    return RecordSet


def return_status_record_set(search_date, progress_code):
    RecordSet = Warehouse.objects.filter(workdate=search_date,
                                         progress__exact=progress_code, )
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


def reset_time(need_time):
    this_hour = need_time[0:2]
    this_mins = need_time[3:5]
    if this_hour != '30' and this_mins != '00':
        if this_mins > '30':
            this_hour = int(this_hour) + 1
            if this_hour < 10:
                this_hour = '0' + str(this_hour)
            this_mins = '00'
        else:
            this_mins = '30'
    new_time = this_hour + ":" + this_mins
    return new_time


# Create your views here.
class SlotListView(View):
    @user_is_not_staff
    def get(self, request):
        search_date = request.GET.get("searching_date", datetime.date.today())

        # 通过登录的用户，查找到当前操作仓库的最大 Maxslot
        location_result = UserProfile.objects.filter(user_id=request.user.id)
        position = "UK"
        if location_result:
            position = location_result[0].op_position

        location_result = WarehouseProfile.objects.filter(position=position)
        max_slot_number = 0
        if location_result:
            max_slot_number = location_result[0].maxslot

        # 确定时间的slottime
        all_slots0600 = return_record_set(search_date, 1, 6, 0)
        all_slots0630 = return_record_set(search_date, 1, 6, 30)
        all_slots0700 = return_record_set(search_date, 1, 7, 0)
        all_slots0730 = return_record_set(search_date, 1, 7, 30)
        all_slots0800 = return_record_set(search_date, 1, 8, 0)
        all_slots0830 = return_record_set(search_date, 1, 8, 30)
        all_slots0900 = return_record_set(search_date, 1, 9, 0)
        all_slots0930 = return_record_set(search_date, 1, 9, 30)
        all_slots1000 = return_record_set(search_date, 1, 10, 0)
        all_slots1030 = return_record_set(search_date, 1, 10, 30)
        all_slots1100 = return_record_set(search_date, 1, 11, 0)
        all_slots1130 = return_record_set(search_date, 1, 11, 30)
        all_slots1200 = return_record_set(search_date, 1, 12, 0)
        all_slots1230 = return_record_set(search_date, 1, 12, 30)
        all_slots1300 = return_record_set(search_date, 1, 13, 0)
        all_slots1330 = return_record_set(search_date, 1, 13, 30)
        all_slots1400 = return_record_set(search_date, 1, 14, 0)
        all_slots1430 = return_record_set(search_date, 1, 14, 30)
        all_slots1500 = return_record_set(search_date, 1, 15, 0)
        all_slots1530 = return_record_set(search_date, 1, 15, 30)
        all_slots1600 = return_record_set(search_date, 1, 16, 0)
        all_slots1630 = return_record_set(search_date, 1, 16, 30)
        all_slots1700 = return_record_set(search_date, 1, 17, 0)
        all_slots1730 = return_record_set(search_date, 1, 17, 30)
        all_slots1800 = return_record_set(search_date, 1, 18, 0)
        all_slots1830 = return_record_set(search_date, 1, 18, 30)
        all_slots1900 = return_record_set(search_date, 1, 19, 0)
        all_slots1930 = return_record_set(search_date, 1, 19, 30)
        all_slots2000 = return_record_set(search_date, 1, 20, 0)
        all_slots2030 = return_record_set(search_date, 1, 20, 30)

        # 没有确定时间的INBOUND
        all_NoInSlotsTimes = Warehouse.objects.filter(workdate=search_date,
                                                      havetime__exact=0,
                                                      status__exact="INBOUND",
                                                      ).order_by("hailerid")
        # 没有确定时间的OUTBOUND
        all_NoOutSlotsTimes = Warehouse.objects.filter(workdate=search_date,
                                                       havetime__exact=0,
                                                       status__exact="OUTBOUND",
                                                       ).order_by("hailerid")

        # 取得所有车辆的状态情况
        all_progress_arrived = return_status_record_set(search_date, 2)
        all_progress_loading = return_status_record_set(search_date, 3)
        all_progress_finished = return_status_record_set(search_date, 4)
        all_progress_abnormal = return_status_record_set(search_date, 5)

        # 取得hailer的数据
        all_Hailers = Haulier.objects.all()

        return render(request, "SlotList.html", {
            "searching_date": search_date,
            "all_slots0600": all_slots0600, "all_slots0630": all_slots0630,
            "all_slots0700": all_slots0700, "all_slots0730": all_slots0730,
            "all_slots0800": all_slots0800, "all_slots0830": all_slots0830,
            "all_slots0900": all_slots0900, "all_slots0930": all_slots0930,
            "all_slots1000": all_slots1000, "all_slots1030": all_slots1030,
            "all_slots1100": all_slots1100, "all_slots1130": all_slots1130,
            "all_slots1200": all_slots1200, "all_slots1230": all_slots1230,
            "all_slots1300": all_slots1300, "all_slots1330": all_slots1330,
            "all_slots1400": all_slots1400, "all_slots1430": all_slots1430,
            "all_slots1500": all_slots1500, "all_slots1530": all_slots1530,
            "all_slots1600": all_slots1600, "all_slots1630": all_slots1630,
            "all_slots1700": all_slots1700, "all_slots1730": all_slots1730,
            "all_slots1800": all_slots1800, "all_slots1830": all_slots1830,
            "all_slots1900": all_slots1900, "all_slots1930": all_slots1930,
            "all_slots2000": all_slots2000, "all_slots2030": all_slots2030,
            "all_NoInSlotsTimes": all_NoInSlotsTimes, "all_NoOutSlotsTimes": all_NoOutSlotsTimes,
            "all_Hailers": all_Hailers,
            "max_slot_number": max_slot_number,
            "all_progress_arrived": all_progress_arrived,
            "all_progress_loading": all_progress_loading,
            "all_progress_finished": all_progress_finished,
            "all_progress_abnormal": all_progress_abnormal,

        })

    @user_is_not_staff
    def post(self, request):
        Warehouse_form = SlotTimeForm(request.POST)
        workdate = request.POST.get("workdate", datetime.datetime.now())  # 抵达日期
        # 传达参数
        request.session['searching_date'] = workdate
        if Warehouse_form.is_valid():
            deliveryref = request.POST.get("deliveryref", "")
            haulier = request.POST.get("hailer", 0)  # 承运人
            if deliveryref == "":
                return render(request, "Slot_Save_Error.html",
                              {"Warehouse_form": Warehouse_form,
                               "ErrorMsg": "This Delivery Ref. can not be empty. ",
                               "searching_date": workdate,
                               "slottime": ""
                               })

            tmp_delieryref = haulier + deliveryref
            filter_result = Warehouse.objects.filter(deliveryref__exact=tmp_delieryref)
            if filter_result:
                return render(request, "Slot_Save_Error.html",
                              {"Warehouse_form": Warehouse_form,
                               "ErrorMsg": "This Delivery Ref. is Existed",
                               "searching_date": workdate,
                               "slottime": ""
                               })

            # 根据用户能够操作的地点， 判断仓库的位置
            position = request.user.profile.op_position  # 仓库位置
            yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
            d_workdate = datetime.datetime.strptime(workdate, "%Y-%m-%d")

            if d_workdate < yesterday:
                strError = "You can not select the date before today. "
                return render(request, "Slot_Save_Error.html",
                              {"deliveryref": deliveryref,
                               "searching_date": workdate,
                               "slottime": "",
                               "ErrorMsg": strError,
                               })

            # 不能更新成为当前日期之后10天的日期
            last_day = 10
            diff_day = (d_workdate - yesterday).days
            if diff_day >= last_day:
                strError = " You cannot set the date more than 10 days after the current date"
                return render(request, "Slot_Save_Error.html",
                              {"Warehouse_form": Warehouse_form,
                               "searching_date": workdate,
                               "slottime": '',
                               "ErrorMsg": strError,
                               })

            hailer_result = Haulier.objects.filter(code__exact=haulier)
            hailer_id = 0
            if hailer_result:
                hailer_id = hailer_result[0].id  # 承运人id

            # 判断时间，并转换成为整点 00 或 30
            slottime = request.POST.get("slottime", 0)  # 承运时间
            time_result = WarehouseProfile.objects.filter(position__exact=position)
            begin_time = datetime.time(0).strftime("%H:%M")
            over_time = datetime.time(0).strftime("%H:%M")
            if time_result:
                begin_time = time_result[0].beginworktime.strftime("%H:%M")
                over_time = time_result[0].overworktime.strftime("%H:%M")

            if slottime < begin_time or slottime > over_time:
                strError = "We are opening time is " + begin_time + " to  " + over_time + \
                           ", Please check your input time ( " + slottime + ")"
                return render(request, "Slot_Save_Error.html",
                              {"Warehouse_form": Warehouse_form,
                               "searching_date": workdate,
                               "slottime": slottime,
                               "ErrorMsg": strError,
                               })

            slottime = reset_time(slottime)
            slot_hour = slottime[0:2]
            slot_mins = slottime[3:5]

            vehiclereg = request.POST.get("vehiclereg", 0)  # 车牌号码
            status = request.POST.get("status", 0)  # INBOUND OR OUTBOUND
            havetime = request.POST.get("haveTime", 1)  # 是否确定时间， 0 未确定， 1 确定

            # 需要在此判断， 该时间段是否已经满了？
            if position == "UK" and havetime == 1:
                warehouse_profile_result = WarehouseProfile.objects.filter(position=position)
                max_count = 0
                max_inbound_count = 0
                if warehouse_profile_result:
                    max_count = warehouse_profile_result[0].maxslot
                    max_inbound_count = warehouse_profile_result[0].maxinbound

                # 检查是否有预留的公司时间
                weekday = datetime.datetime.strptime(workdate, '%Y-%m-%d').weekday() + 1
                check_date_result = FixWeekday.objects.filter(weekday=weekday,
                                                              time__hour=slot_hour,
                                                              time__minute=slot_mins,
                                                              status=1)
                count_preserves = 0
                if check_date_result:
                    count_preserves = check_date_result.count()

                # 检查该时间段， 有多少台车已经booking
                warehouse_result = Warehouse.objects.filter(workdate=workdate,
                                                            slottime__hour=slot_hour,
                                                            slottime__minute=slot_mins,
                                                            havetime__exact=1)
                count_orders = 0
                if warehouse_result:
                    count_orders = warehouse_result.count()

                if count_orders + count_preserves >= max_count:
                    strError = "Max handle number is " + str(max_count) + \
                               ". But System already have booking number is " + \
                               str(count_orders) + " and Preserves number is " + str(count_preserves)
                    return render(request, "Slot_Save_Error.html",
                                  {"Warehouse_form": Warehouse_form,
                                   "searching_date": workdate,
                                   "slottime": slottime,
                                   "ErrorMsg": strError
                                   })

                if status == "INBOUND":
                    # 检查该时间段， 最大的INBOUND的数量是否已经爆满
                    warehouse_result = Warehouse.objects.filter(workdate=workdate,
                                                                slottime__hour=slot_hour,
                                                                slottime__minute=slot_mins,
                                                                havetime__exact=1,
                                                                status="INBOUND")
                    count_inbound_order = warehouse_result.count()
                    if count_inbound_order >= max_inbound_count:
                        strError = "INBOUND NUMBER IS FULL, Because We only can handle Max Inbound number is " + str(
                            max_inbound_count)
                        return render(request, "Slot_Save_Error.html",
                                      {"Warehouse_form": Warehouse_form,
                                       "searching_date": workdate,
                                       "slottime": slottime,
                                       "ErrorMsg": strError})
            new_ref = haulier + deliveryref.upper()
            warehouse = Warehouse()
            warehouse.deliveryref = new_ref
            warehouse.workdate = workdate
            warehouse.slottime = slottime
            warehouse.vehiclereg = vehiclereg.upper()
            warehouse.status = status.upper()
            warehouse.progress = 1  # 1=Booked 2=Arrived 3=Loading 4=Finished 5=abnormal
            warehouse.havetime = havetime
            warehouse.hailerid_id = hailer_id
            warehouse.position = position
            warehouse.op_user_id = request.user.id
            warehouse.op_datetime = timezone.now()
            warehouse.save()

            progressRecord = ProgressRecord()
            progressRecord.deliveryref = haulier + deliveryref.upper()
            progressRecord.progress = 1  # 1=Booked 2=Arrived 3=Loading 4=Finished 5=abnormal
            progressRecord.position = position
            progressRecord.op_user_id = request.user.id
            progressRecord.progress_name = "1-Booked"
            progressRecord.remark = "Create Booked"
            progressRecord.save()

            # return render(request, "Slot_Save_Success.html",
            #               {"Warehouse_form": Warehouse_form,
            #                "searching_date": workdate,
            #                "slottime": slottime,
            #                })
            pk = Warehouse.objects.filter(deliveryref__exact=new_ref)[0].id
            return redirect('slot:slot_detail', pk=pk)
        else:
            strError = "Delivery Reference can not be repeated or empty. "
            return render(request, "Slot_Save_Error.html",
                          {"Warehouse_form": Warehouse_form,
                           "searching_date": workdate,
                           "slottime": "",
                           "ErrorMsg": strError})


class SlotDetailView(DetailView):
    queryset = Warehouse.objects.all()
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
        Warehouse_Updateform = SlotTimeUpdateForm(request.POST)
        new_workdate = request.POST.get("new_workdate", 0)  # 新抵达日期
        if Warehouse_Updateform.is_valid():
            is_update_progress = False  # 变更状态初始值为假
            deliveryref = request.POST.get("deliveryref", "")
            slot_result = Warehouse.objects.filter(deliveryref=deliveryref)
            if slot_result:
                pk = slot_result[0].id
                new_time = request.POST.get("new_slottime", 0)  # 新旧抵达时间
                old_workdate = slot_result[0].workdate
                old_time = slot_result[0].slottime
                old_havetime = slot_result[0].havetime
                status = slot_result[0].status
                old_progress = str(slot_result[0].progress)
                old_remark = slot_result[0].remark.strip()
                new_remark = request.POST.get("new_remark", "").strip()  # 新备注
                remark_reason = ""  # 记录修改的原因
                progress_name = get_progress_name(old_progress)
                new_progress = old_progress
                progress = old_progress
                if request.user.profile.staff_role != 1:  # 只有仓库人员或经理才能更新状态
                    if new_workdate == 0:  # 仓库人员进入后，日期读数将为0， 重置新日期及时间
                        new_workdate = datetime.datetime.strftime(old_workdate, "%Y-%m-%d")
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
                                strError = "You can not change the progress from " + old_progress_name + \
                                           " To " + progress_name + ". "
                                return render(request, "Slot_Save_Error.html",
                                              {"Warehouse_form": Warehouse_Updateform,
                                               "workdate": new_workdate,
                                               "slottime": new_time,
                                               "ErrorMsg": strError,
                                               })

                havetime = request.POST.get("new_haveTime", 1)  # 是否确定时间， 0 未确定， 1 确定

                if old_havetime != havetime:
                    remark_reason = remark_reason + " | Modify Have Time: From " + str(old_havetime) \
                                    + " To " + str(havetime)  # 记录修改是否确定时间

                if havetime == 1:  # 有确定的时间，才去判断仓库是否能够接受
                    compare_olddate = datetime.datetime.strftime(old_workdate, "%Y-%m-%d")
                    compare_oldtime = old_time.strftime("%H:%M")[0:5]

                    if not (new_workdate == compare_olddate and new_time == compare_oldtime):
                        remark_reason = remark_reason + " | Modify DateTime: From " + compare_olddate + \
                                        " " + compare_oldtime + " To " + new_workdate + " " + new_time  # 记录修改时间
                        position = request.user.profile.op_position  # 仓库位置
                        yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
                        d_workdate = datetime.datetime.strptime(new_workdate, "%Y-%m-%d")
                        # 不能更新成为当前日期之前的日期
                        if d_workdate < yesterday:
                            strError = "You can not select the date before today. "
                            return render(request, "Slot_Save_Error.html",
                                          {"Warehouse_form": Warehouse_Updateform,
                                           "searching_date": old_workdate,
                                           "slottime": new_time,
                                           "ErrorMsg": strError,
                                           })

                        # 不能更新成为当前日期之后10天的日期
                        last_day = 10
                        diff_day = (d_workdate - yesterday).days
                        if diff_day >= last_day:
                            strError = " You cannot set the date more than 10 days after the current date"
                            return render(request, "Slot_Save_Error.html",
                                          {"Warehouse_form": Warehouse_Updateform,
                                           "searching_date": old_workdate,
                                           "slottime": new_time,
                                           "ErrorMsg": strError,
                                           })

                        # 判断时间，并转换成为整点 00 或 30
                        time_result = WarehouseProfile.objects.filter(position__exact=position)
                        begin_time = datetime.time(0).strftime("%H:%M")
                        over_time = datetime.time(0).strftime("%H:%M")
                        if time_result:
                            begin_time = time_result[0].beginworktime.strftime("%H:%M")
                            over_time = time_result[0].overworktime.strftime("%H:%M")

                        if new_time < begin_time or new_time > over_time:
                            strError = "We are opening time is " + begin_time + " to  " + over_time + \
                                       ", Please check your input time ( " + new_time + ")"
                            return render(request, "Slot_Save_Error.html",
                                          {"Warehouse_form": Warehouse_Updateform,
                                           "searching_date": new_workdate,
                                           "slottime": new_time,
                                           "ErrorMsg": strError,
                                           })

                        new_time = reset_time(new_time)
                        slot_hour = new_time[0:2]
                        slot_mins = new_time[3:5]

                        # 需要在此判断， 该时间段是否已经满了？
                        if new_progress == old_progress:  # 如果是修改状态，则不必要判断是否满了
                            if position == "UK" and havetime == 1:
                                warehouse_profile_result = WarehouseProfile.objects.filter(position=position)
                                max_count = 0
                                max_inbound_count = 0
                                if warehouse_profile_result:
                                    max_count = warehouse_profile_result[0].maxslot
                                    max_inbound_count = warehouse_profile_result[0].maxinbound

                                # 检查是否有预留的公司时间
                                weekday = datetime.datetime.strptime(new_workdate, '%Y-%m-%d').weekday() + 1
                                check_date_result = FixWeekday.objects.filter(weekday=weekday,
                                                                              time__hour=slot_hour,
                                                                              time__minute=slot_mins,
                                                                              status=1)
                                count_preserves = 0
                                if check_date_result:
                                    count_preserves = check_date_result.count()

                                # 检查该时间段， 有多少台车已经booking
                                warehouse_result = Warehouse.objects.filter(workdate=new_workdate,
                                                                            slottime__hour=slot_hour,
                                                                            slottime__minute=slot_mins,
                                                                            havetime__exact=1)
                                count_orders = 0
                                if warehouse_result:
                                    count_orders = warehouse_result.count()

                                if count_orders + count_preserves >= max_count:
                                    strError = "Max handle number is " + str(max_count) + \
                                               ". But System already have booking number is " + \
                                               str(count_orders) + " and Preserves number is " + str(count_preserves)
                                    return render(request, "Slot_Save_Error.html",
                                                  {"Warehouse_form": Warehouse_Updateform,
                                                   "searching_date": new_workdate,
                                                   "slottime": new_time,
                                                   "ErrorMsg": strError
                                                   })

                                if status == "INBOUND":
                                    # 检查该时间段， 最大的INBOUND的数量是否已经爆满
                                    warehouse_result = Warehouse.objects.filter(workdate=new_workdate,
                                                                                slottime__hour=slot_hour,
                                                                                slottime__minute=slot_mins,
                                                                                havetime__exact=1,
                                                                                status="INBOUND")
                                    count_inbound_order = warehouse_result.count()
                                    if count_inbound_order >= max_inbound_count:
                                        strError = "INBOUND NUMBER IS FULL, Because We only can handle Max Inbound " \
                                                   "number is " + str(max_inbound_count)
                                        return render(request, "Slot_Save_Error.html",
                                                      {"Warehouse_form": Warehouse_Updateform,
                                                       "searching_date": new_workdate,
                                                       "slottime": new_time,
                                                       "ErrorMsg": strError})

                if old_remark != new_remark:
                    remark_reason = remark_reason + " | Modify Remark: From " + old_remark \
                                    + " To " + new_remark  # 记录修改备注

                if remark_reason != "":
                    warehouse = Warehouse.objects.get(deliveryref=deliveryref)
                    warehouse.workdate = new_workdate
                    warehouse.slottime = new_time
                    warehouse.havetime = havetime
                    warehouse.progress = int(progress)  # 1=Booked 2=Arrived 3=Loading 4=Finished 5=Abnormal
                    warehouse.remark = new_remark
                    warehouse.save()

                    progressRecord = ProgressRecord()
                    progressRecord.deliveryref = deliveryref
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
                        if progress == '2':  # 2 - Arrived
                            system_sendmail(deliveryref, op_name, file_list, email_to_list, 'Arrived', )
                        elif progress == '4':  # 4 - Finished
                            system_sendmail(deliveryref, op_name, file_list, email_to_list, 'Finished', )

                return redirect('slot:slot_detail', pk=pk)
        else:
            strError = "Delivery Reference can not be repeated or empty. "
            return render(request, "Slot_Save_Error.html",
                          {"Warehouse_form": Warehouse_Updateform,
                           "searching_date": new_workdate,
                           "slottime": "",
                           "ErrorMsg": strError})


class SlotTimeDeleteView(DeleteView):
    model = Warehouse
    template_name = "Slot_Confirm_Delete.html"

    @user_is_not_staff
    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(SlotTimeDeleteView, self).get_object()
        # if not obj.op_user == self.request.user.id:
        #     raise Http404
        return obj

    @user_is_not_staff
    def get_success_url(self):
        return reverse('slot:slot_list')


class SlotSearchListView(ListView):
    model = Warehouse
    template_name = 'slot_search_list.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        query_delivery = self.request.GET.get('s_delivery', '')
        query_progress = self.request.GET.get('progress', '0')
        query_haulier = int(self.request.GET.get('s_haulier', '0'))
        data['all_haulier'] = Haulier.objects.all()
        data['query_delivery'] = query_delivery
        data['query_progress'] = query_progress
        data['query_haulier'] = query_haulier

        return data

    def get_queryset(self):
        query_delivery = self.request.GET.get('s_delivery', '')
        query_progress = self.request.GET.get('progress', '0')
        query_haulier = self.request.GET.get('s_haulier', '0')

        result_list = []
        if not (query_haulier == '0' and query_progress == '0' and query_delivery == ''):  # 三个条件任意有一个
            if query_haulier != '0' and query_progress != '0' and query_delivery:  # 三个条件均有
                query1 = Q(deliveryref__icontains=query_delivery)
                query2 = Q(progress__exact=query_progress)
                query3 = Q(hailerid__id=query_haulier)
                result_list = Warehouse.objects.filter(query1 & query2 & query3).order_by('-workdate', 'slottime')

            if query_haulier == '0' and query_progress == '0' and query_delivery:  # 只是查询 Delivery Ref.
                query = Q(deliveryref__icontains=query_delivery)
                result_list = Warehouse.objects.filter(query).order_by('-workdate', 'slottime')

            if query_haulier != '0' and query_progress == '0' and not query_delivery:  # 只是查询 Haulier.
                query = Q(hailerid__id=query_haulier)
                result_list = Warehouse.objects.filter(query).order_by('-workdate', 'slottime')

            if query_haulier == '0' and query_progress != '0' and not query_delivery:  # 只是查询 Progress.
                query = Q(progress__contains=query_progress)
                result_list = Warehouse.objects.filter(query).order_by('-workdate', 'slottime')

            # 两两组合
            if query_haulier != '0' and query_progress == '0' and query_delivery:  # 只是查询 Delivery Ref. haulier
                query1 = Q(deliveryref__icontains=query_delivery)
                query3 = Q(hailerid__id=query_haulier)
                result_list = Warehouse.objects.filter(query1 & query3).order_by('-workdate', 'slottime')

            if query_haulier != '0' and query_progress != '0' and not query_delivery:  # 只是查询 progress. haulier
                query2 = Q(progress__exact=query_progress)
                query3 = Q(hailerid__id=query_haulier)
                result_list = Warehouse.objects.filter(query2 & query3).order_by('-workdate', 'slottime')

            if query_haulier == '0' and query_progress != '0' and query_delivery:  # 只是查询 progress. Delivery Ref.
                query1 = Q(deliveryref__icontains=query_delivery)
                query2 = Q(progress__exact=query_progress)
                result_list = Warehouse.objects.filter(query1 & query2).order_by('-workdate', 'slottime')

        else:
            result_list = Warehouse.objects.all().order_by('-workdate', 'slottime')

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
                system_sendmail(ref, op_name, file_list, email_to_list, send_type)

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
