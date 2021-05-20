import datetime

from django.shortcuts import render
from django.views import View

from menu.views import get_user_grant_list
from ocean.forms import FbaQuoteForm, PrivateQuoteForm, CabinetQuoteForm
from ocean.models import OceanPortModel, AmazonPriceModel, FbaItemPriceModel, ContainModel, CabinetItemPriceModel
from ocean.models import PrivateItemPriceModel
from ocean.calculation import calc_bulk_fba, calc_cabinet, judge_cabinet_input, calc_private

MENU_ACTIVE = 'OCEAN'


# 海运散货 FBA
class OceanCalcFbaView(View):
    def get(self, request):
        page_tab = 1
        all_port = OceanPortModel.objects.all()
        amazon_warehouse = AmazonPriceModel.objects.all()

        context = {'page_tab': page_tab,
                   'menu_active': MENU_ACTIVE,
                   'all_port': all_port,
                   'amazon_warehouse': amazon_warehouse,
                   'menu_grant': get_user_grant_list(self.request.user.id),
                   }
        return render(request, 'fba/ocean_fba.html', context=context, )

    def post(self, request):
        page_tab = 1
        forms = FbaQuoteForm(request.POST)
        find_error = False
        error_msg = ''
        warehouse_data = []
        warehouse_code_list = []
        for i in range(10):
            code = 'fba_code' + str(i) + '_amsify'
            volume = 'volume' + str(i)
            weight = 'weight' + str(i)
            warehouse_code = request.POST.get(code, 'NO-DATA')
            warehouse_volume = request.POST.get(volume, 'NO-DATA')
            warehouse_weight = request.POST.get(weight, 'NO-DATA')
            # 判断仓库及体积是否均有输入及是否有重复输入的仓库代码
            if warehouse_code == '':
                find_error = True
                error_msg = '请选择需要派送的亚马逊仓库代码'
                warehouse_data.append([warehouse_code, warehouse_volume, warehouse_weight, ])
            else:
                if warehouse_code != 'NO-DATA' and warehouse_volume != 'NO-DATA':
                    warehouse_data.append([warehouse_code, warehouse_volume, warehouse_weight, ])
                elif warehouse_code == 'NO-DATA' and warehouse_volume == 'NO-DATA':
                    pass
                else:
                    find_error = True
                    error_msg = '请选择需要派送的亚马逊仓库代码'
                    warehouse_data.append([warehouse_code, warehouse_volume, warehouse_weight, ])

            if warehouse_code in warehouse_code_list:
                find_error = True
                error_msg = '仓库代码有重复，请检查'
            else:
                if warehouse_code != 'NO-DATA':
                    warehouse_code_list.append(warehouse_code)

        if forms.is_valid() and (not find_error):  # 没有发现错误
            # 开始计算，获取结果
            try:
                first_delivery = forms.data['first_delivery']
            except:
                first_delivery = '0'

            input_data = {'port': forms.data['port'],
                          'hs_code_number': int(forms.data['hs_code_number']),
                          'fba_number': int(forms.data['fba_number']),
                          'first_delivery': first_delivery,
                          'warehouse_data': warehouse_data,
                          }
            # 开始计算，并取到返回的结果
            result_data = calc_bulk_fba(request, input_data)
            all_surcharge = FbaItemPriceModel.objects.filter(fee_type=1)
            context = {'page_tab': page_tab,
                       'menu_active': MENU_ACTIVE,
                       'all_surcharge': all_surcharge,
                       'input_data': input_data,
                       'menu_grant': get_user_grant_list(self.request.user.id),
                       'result_data': result_data
                       }
            return render(request, 'fba/ocean_fba_quotation.html', context=context, )

        # 发现有错误
        all_port = OceanPortModel.objects.all()
        amazon_warehouse = AmazonPriceModel.objects.all()
        context = {'page_tab': page_tab,
                   'menu_active': MENU_ACTIVE,
                   'all_port': all_port,
                   'amazon_warehouse': amazon_warehouse,
                   'warehouse_data': warehouse_data,
                   'forms': forms,
                   'error_msg': error_msg,
                   'menu_grant': get_user_grant_list(self.request.user.id),
                   }
        return render(request, 'fba/ocean_fba.html', context=context, )


# 海运散货私人仓费用查询
class OceanCalcPrivateView(View):
    def get(self, request):
        page_tab = 3
        all_port = OceanPortModel.objects.all()

        context = {'page_tab': page_tab,
                   'menu_grant': get_user_grant_list(self.request.user.id),
                   'menu_active': MENU_ACTIVE,
                   'all_port': all_port,
                   }
        return render(request, 'private/ocean_private.html', context=context, )

    def post(self, request):
        page_tab = 3
        forms = PrivateQuoteForm(request.POST)
        if forms.is_valid():  # 没有发现错误
            # 开始计算，并取到返回的结果
            result_data = calc_private(request, forms)
            all_surcharge = PrivateItemPriceModel.objects.filter(fee_type=1)
            context = {'page_tab': page_tab,
                       'menu_active': MENU_ACTIVE,
                       'all_surcharge': all_surcharge,
                       'result_data': result_data,
                       'menu_grant': get_user_grant_list(self.request.user.id),
                       }
            return render(request, 'private/ocean_private_quotation.html', context=context, )

        # 发现有错误
        all_port = OceanPortModel.objects.all()
        context = {'page_tab': page_tab,
                   'menu_active': MENU_ACTIVE,
                   'all_port': all_port,
                   'menu_grant': get_user_grant_list(self.request.user.id),
                   'forms': forms,
                   }
        return render(request, 'private/ocean_private.html', context=context, )


# 海运整柜费用查询
class OceanCalcCabinetView(View):
    def get(self, request):
        page_tab = 2
        all_port = OceanPortModel.objects.all()
        amazon_warehouse = AmazonPriceModel.objects.all()
        container_type = ContainModel.objects.all()

        context = {'page_tab': page_tab,
                   'menu_active': MENU_ACTIVE,
                   'menu_grant': get_user_grant_list(self.request.user.id),
                   'all_port': all_port,
                   'amazon_warehouse': amazon_warehouse,
                   'container_type': container_type,
                   }
        return render(request, 'cabinet/ocean_cabinet.html', context=context, )

    def post(self, request):
        page_tab = 2
        forms = CabinetQuoteForm(request.POST)
        result = judge_cabinet_input(request, forms)
        cabinet_data = result[0]
        error_msg = result[1]

        if forms.is_valid() and not error_msg:  # 没有发现错误
            input_data = {'port': forms.data['port'],
                          'hs_code_number': int(forms.data['hs_code_number']),
                          'cabinet_data': cabinet_data,
                          }
            # 开始计算海运整柜，获取结果
            result_data = calc_cabinet(request, input_data)
            all_surcharge = CabinetItemPriceModel.objects.filter(fee_type=1).order_by('id')
            container_type = ContainModel.objects.all()
            context = {'page_tab': page_tab,
                       'menu_active': MENU_ACTIVE,
                       'all_surcharge': all_surcharge,
                       'container_type': container_type,
                       'input_data': input_data,
                       'menu_grant': get_user_grant_list(self.request.user.id),
                       'result_data': result_data
                       }
            return render(request, 'cabinet/ocean_cabinet_quotation.html', context=context, )

        # 发现有整柜输入有错误
        all_port = OceanPortModel.objects.all()
        amazon_warehouse = AmazonPriceModel.objects.all()
        container_type = ContainModel.objects.all()

        context = {'page_tab': page_tab,
                   'menu_active': MENU_ACTIVE,
                   'all_port': all_port,
                   'amazon_warehouse': amazon_warehouse,
                   'container_type': container_type,
                   'cabinet_data': cabinet_data,
                   'forms': forms,
                   'menu_grant': get_user_grant_list(self.request.user.id),
                   'error_msg': error_msg,
                   }
        return render(request, 'cabinet/ocean_cabinet.html', context=context, )

