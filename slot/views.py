import datetime
from django.shortcuts import render, reverse
from django.http import Http404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView
from .forms import SoltTimeForm, SoltTimeUpdateForm
from .models import Warehouse, Haulier, WarehouseProfile, FixWeekday, ProgressRecord
from users.models import UserProfile


# Create your views here.
class SoltListView(View):
    def get(self, request):
        search_date = request.GET.get("searching_date")

        if search_date is None or search_date == "":
            search_date = datetime.date.today()

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
        all_slots0600 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=6,
                                                 slottime__minute=0,
                                                 ).order_by("status")

        all_slots0630 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=6,
                                                 slottime__minute=30,
                                                 ).order_by("status")
        all_slots0700 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=7,
                                                 slottime__minute=0,
                                                 ).order_by("status")
        all_slots0730 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=7,
                                                 slottime__minute=30,
                                                 ).order_by("status")
        all_slots0800 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=8,
                                                 slottime__minute=0,
                                                 ).order_by("status")
        all_slots0830 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=8,
                                                 slottime__minute=30,
                                                 ).order_by("status")
        all_slots0900 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=9,
                                                 slottime__minute=0,
                                                 ).order_by("status")
        all_slots0930 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=9,
                                                 slottime__minute=30,
                                                 ).order_by("status")
        all_slots1000 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=10,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1030 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=10,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1100 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=11,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1130 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=11,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1200 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=12,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1230 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=12,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1300 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=13,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1330 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=13,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1400 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=14,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1430 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=14,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1500 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=15,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1530 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=15,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1600 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=16,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1630 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=16,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1700 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=17,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1730 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=17,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1800 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=18,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1830 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=18,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots1900 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=19,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots1930 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=19,
                                                 slottime__minute=30
                                                 ).order_by("status")
        all_slots2000 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=20,
                                                 slottime__minute=00
                                                 ).order_by("status")
        all_slots2030 = Warehouse.objects.filter(workdate=search_date,
                                                 havetime__exact=1,
                                                 slottime__hour=20,
                                                 slottime__minute=30
                                                 ).order_by("status")
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

        # 取得hailer的数据
        all_Hailers = Haulier.objects.all()

        return render(request, "SlotList.html", {
            "search_date": search_date,
            "all_slots0600": all_slots0600,
            "all_slots0630": all_slots0630,
            "all_slots0700": all_slots0700,
            "all_slots0730": all_slots0730,
            "all_slots0800": all_slots0800,
            "all_slots0830": all_slots0830,
            "all_slots0900": all_slots0900,
            "all_slots0930": all_slots0930,
            "all_slots1000": all_slots1000,
            "all_slots1030": all_slots1030,
            "all_slots1100": all_slots1100,
            "all_slots1130": all_slots1130,
            "all_slots1200": all_slots1200,
            "all_slots1230": all_slots1230,
            "all_slots1300": all_slots1300,
            "all_slots1330": all_slots1330,
            "all_slots1400": all_slots1400,
            "all_slots1430": all_slots1430,
            "all_slots1500": all_slots1500,
            "all_slots1530": all_slots1530,
            "all_slots1600": all_slots1600,
            "all_slots1630": all_slots1630,
            "all_slots1700": all_slots1700,
            "all_slots1730": all_slots1730,
            "all_slots1800": all_slots1800,
            "all_slots1830": all_slots1830,
            "all_slots1900": all_slots1900,
            "all_slots1930": all_slots1930,
            "all_slots2000": all_slots2000,
            "all_slots2030": all_slots2030,
            "all_NoInSlotsTimes": all_NoInSlotsTimes,
            "all_NoOutSlotsTimes": all_NoOutSlotsTimes,
            "all_Hailers": all_Hailers,
            "max_slot_number": max_slot_number,
        })

    def post(self, request):
        Warehouse_form = SoltTimeForm(request.POST)
        if Warehouse_form.is_valid():
            deliveryref = request.POST.get("deliveryref", "")
            hailer = request.POST.get("hailer", 0)  # 承运人
            if deliveryref == "":
                return render(request, "Slot_Save_Error.html",
                              {"Warehouse_form": Warehouse_form,
                               "ErrorMsg": "This Delivery Ref. can not be empty. ",
                               "workdate": "",
                               "slottime": ""
                               })

            tmp_delieryref = hailer + deliveryref
            filter_result = Warehouse.objects.filter(deliveryref__exact=tmp_delieryref)
            if filter_result:
                return render(request, "Slot_Save_Error.html",
                              {"Warehouse_form": Warehouse_form,
                               "ErrorMsg": "This Delivery Ref. is Existed",
                               "workdate": "",
                               "slottime": ""
                               })

            username = request.user.username  # 用户名

            # 根据用户能够操作的地点， 判断仓库的位置
            position_result = UserProfile.objects.filter(user_id=request.user.id)
            position = "UK"
            op_role = 1
            op_telephone = ""
            op_email = request.user.email
            if position_result:
                position = position_result[0].op_position  # 仓库位置
                op_role = position_result[0].staff_role  # 角色
                op_telephone = position_result[0].telephone  # 电话

            workdate = request.POST.get("workdate", 0)  # 抵达日期
            yesterday = datetime.datetime.now()+datetime.timedelta(days=-1)
            str_yesterday = yesterday.strftime("%Y-%m-%d")
            d_workdate = datetime.datetime.strptime(workdate, "%Y-%m-%d")

            if d_workdate < yesterday:
                strError = "You can not select the date before today. "
                return render(request, "Slot_Save_Error.html",
                              {"Warehouse_form": Warehouse_form,
                               "workdate": "",
                               "slottime": "",
                               "ErrorMsg": strError,
                               })

            hailer_result = Haulier.objects.filter(code__exact=hailer)
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
                               "workdate": workdate,
                               "slottime": slottime,
                               "ErrorMsg": strError,
                               })

            slot_hour = slottime[0:2]
            slot_mins = slottime[3:5]
            if slot_mins != '30' and slot_mins != '00':
                if slot_mins > '30':
                    slot_hour = int(slot_hour) + 1
                    if slot_hour < 10:
                        slot_hour = '0'+str(slot_hour)
                    slot_mins = '00'
                else:
                    slot_mins = '30'

            slottime = slot_hour+":"+slot_mins

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
                weekday = datetime.datetime.strptime(workdate, '%Y-%m-%d').weekday()+1
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
                                   "workdate": workdate,
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
                        strError = "INBOUND NUMBER IS FULL, Because We only can handle Max Inbound number is " + str(max_inbound_count)
                        return render(request, "Slot_Save_Error.html",
                                      {"Warehouse_form": Warehouse_form,
                                       "workdate": workdate,
                                       "slottime": slottime,
                                       "ErrorMsg": strError})

            warehouse = Warehouse()
            warehouse.deliveryref = hailer + deliveryref.upper()
            warehouse.workdate = workdate
            warehouse.slottime = slottime
            warehouse.vehiclereg = vehiclereg.upper()
            warehouse.status = status.upper()
            warehouse.progress = 1  # 1=Booked 2=Arrived 3=Loading 4=Finished 5=abnormal
            warehouse.havetime = havetime
            warehouse.hailerid = hailer_id
            warehouse.position = position
            warehouse.op_user = request.user.id
            warehouse.op_telephone = op_telephone
            warehouse.op_email = op_email
            warehouse.op_role = op_role
            warehouse.save()

            progressRecord = ProgressRecord()
            progressRecord.deliveryref = hailer + deliveryref.upper()
            progressRecord.progress = 1  # 1=Booked 2=Arrived 3=Loading 4=Finished 5=abnormal
            progressRecord.position = position
            progressRecord.op_role = op_role
            progressRecord.op_telephone = op_telephone
            progressRecord.op_email =op_email
            progressRecord.progress_name = "Booked"
            progressRecord.remark = "Create Booked"
            progressRecord.save()
            return render(request, "Slot_Save_Success.html", {"searching_date": workdate,
                                                              })
        else:
            strError = "Delivery Reference can not be repeated or empty. "
            return render(request, "Slot_Save_Error.html",
                          {"Warehouse_form": Warehouse_form,
                           "workdate": "",
                           "slottime": "",
                           "ErrorMsg": strError})


class SoltDetailView(DetailView):
    queryset = Warehouse.objects.all()
    template_name = "Slot_Detail.html"

    def get_object(self):
        # get_object() 默认时返回通过 pk 或 slug 筛选出的对象（该视图需要操作的对象）
        # Call the superclass
        object = super().get_object()

        return object


# https://blog.csdn.net/tmpbook/article/details/43191177
class SoltUpdateView(View):
    def post(self, request):
        Warehouse_Updateform = SoltTimeUpdateForm(request.POST)
        if Warehouse_Updateform.is_valid():

            deliveryref = request.POST.get("deliveryref", "")
            progress = request.POST.get("progress", "")
            slot_result = Warehouse.objects.filter(deliveryref=deliveryref)
            if slot_result:
                new_workdate = request.POST.get("workdate", 0)  # 新抵达日期
                new_time = request.POST.get("slottime", 0)  # 新旧抵达时间
                old_workdate = slot_result[0].workdate
                old_time = slot_result[0].slottime
                if not(new_workdate == old_workdate and new_time == old_time):

                    # 根据用户能够操作的地点， 判断仓库的位置
                    position_result = UserProfile.objects.filter(user_id=request.user.id)
                    position = "UK"
                    position_id = 1
                    if position_result:
                        position = position_result[0].op_position  # 仓库位置
                        position_id = position_result[0].id

                    yesterday = datetime.datetime.now()+datetime.timedelta(days=-1)
                    str_yesterday = yesterday.strftime("%Y-%m-%d")
                    d_workdate = datetime.datetime.strptime(new_workdate, "%Y-%m-%d")

                    if d_workdate < yesterday:
                        strError = "You can not select the date before today. "
                        return render(request, "Slot_Save_Error.html",
                                      {"Warehouse_form": Warehouse_Updateform,
                                       "workdate": "",
                                       "slottime": "",
                                       "ErrorMsg": strError,
                                       })

                    # 根据用户能够操作的地点， 判断仓库的位置
                    position_result = UserProfile.objects.filter(user_id=request.user.id)
                    position = "UK"
                    position_id = 1

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
                                      {"Warehouse_form": Warehouse_Updateform,
                                       "workdate": old_workdate,
                                       "slottime": slottime,
                                       "ErrorMsg": strError,
                                       })

                    slot_hour = slottime[0:2]
                    slot_mins = slottime[3:5]
                    if slot_mins != '30' and slot_mins != '00':
                        if slot_mins > '30':
                            slot_hour = int(slot_hour) + 1
                            if slot_hour < 10:
                                slot_hour = '0'+str(slot_hour)
                            slot_mins = '00'
                        else:
                            slot_mins = '30'

                    slottime = slot_hour+":"+slot_mins

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
                        weekday = datetime.datetime.strptime(new_workdate, '%Y-%m-%d').weekday()+1
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
                                           "workdate": old_workdate,
                                           "slottime": slottime,
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
                                strError = "INBOUND NUMBER IS FULL, Because We only can handle Max Inbound number is " + str(max_inbound_count)
                                return render(request, "Slot_Save_Error.html",
                                              {"Warehouse_form": Warehouse_Updateform,
                                               "workdate": old_workdate,
                                               "slottime": slottime,
                                               "ErrorMsg": strError})

            warehouse = Warehouse.objects.get(deliveryref=deliveryref)
            warehouse.workdate = new_workdate
            warehouse.slottime = new_time
            warehouse.havetime = havetime
            warehouse.progress = progress  # 1=Create 2=Arrived 3=Loading 4=Finished 5=abnormal
            warehouse.save()
            return render(request,"Slot_Save_Success.html", {"searching_date": new_workdate,
                                                              })
        else:
            strError = "Delivery Reference can not be repeated or empty. "
            return render(request, "Slot_Save_Error.html",
                          {"Warehouse_form": Warehouse_Updateform,
                           "workdate": "",
                           "slottime": "",
                           "ErrorMsg": strError})


class SlotTimeDeleteView(DetailView):
    model = Warehouse
    template_name = "Slot_Confirm_Delete.html"

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(SlotTimeDeleteView, self).get_object()
        # if not obj.op_user == self.request.user.id:
        #     raise Http404
        return obj

    def get_success_url(self):
        return reverse('slot:slot_list')


