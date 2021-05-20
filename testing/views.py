# encoding=utf-8

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views import View

num_progress = 0  # 当前的后台进度值（不喜欢全局变量也可以很轻易地换成别的方法代替）


# 展示界面 UI
def show_progress_page(request):
    # return JsonResponse(num_progress, safe=False)
    return render(request, 'progress.html')


# 后台实际处理程序
def process_data(request):
    global num_progress
    for i in range(12345666):
        # ... Some thing in progress
        num_progress = int(i * 100 / 12345666)  # 更新后台进度值，因为想返回百分数所以乘100
        # print 'num_progress=' + str(num_progress)
        res = num_progress
    return JsonResponse(res, safe=False)


# 前端JS需要访问此程序来更新数据
def show_progress(request):
    print('show_progress----------' + str(num_progress))
    return JsonResponse(num_progress, safe=False)


# 测试弹窗的代码
class TestView(View):
    def p1(request):
        return render(request, "p1.html")

    def p2(request):
        if request.method == "GET":
            return render(request, "p2.html")
        elif request.method == "POST":
            city = request.POST.get("city")
            print(city)
            return render(request, "popup_response.html", {"city": city})


class TestUploadFileView(View):
    def upload_page(request):
        return render(request, 'upload_page_testing.html')  # 这里upload_page便是上面的前端html文件

    def upload(request):
        file = request.FILES  # 一定要调用上传的文件（不管你干嘛，保存也好，啥也不干也好，反正不调用就出错了，
        # 估计是默认不调用就不接收吧。。）才能用ajax上传成功，否则报错，原因不明
        return HttpResponse()


def new_main_page(request):
    return render(request, "amindlte_main_menu.html")


def demo(request):
    return render(request, "index3.html")
