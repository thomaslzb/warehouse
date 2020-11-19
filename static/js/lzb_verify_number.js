//验证输入的是大于零的两位小数或整数
//demo： <input class="form-control col-lg-2 left" id="uk_value"  name="uk_value"   type="text" oninput="verify_decimal2(this)" />
function verify_decimal2(obj){
	// 清除"数字"和"."以外的字符
	obj.value = obj.value.replace(/[^\d.]/g,"");
	// 验证第一个字符是数字
	obj.value = obj.value.replace(/^\./g,"");
	// 只保留第一个, 清除多余的
	obj.value = obj.value.replace(/\.{2,}/g,".");
	obj.value = obj.value.replace(".","$#$").replace(/\./g,"").replace("$#$",".");
	// 只能输入两个小数
	obj.value = obj.value.replace(/^(\-)*(\d+)\.(\d\d).*$/,'$1$2.$3');

	//如果有小数点，不能为类似 1.10的金额
	if(obj.value.indexOf(".")> 0  && obj.value.indexOf("0")>2){
		obj.value= parseFloat(obj.value);
	}
	//如果有小数点，不能为类似 0.00的金额
	if(obj.value.indexOf(".")> 0  && obj.value.lastIndexOf("0")>2){
		obj.value= parseFloat(obj.value);
	}
	 //以上已经过滤，此处控制的是如果没有小数点，首位不能为类似于 01、02的金额
	if (obj.value.indexOf(".") <= 0 && obj.value != "") {
		obj.value = parseFloat(obj.value);
	}
  }

// 验证仅仅能够输入正整数
// onkeyup="onlyNumber(this)" onafterpaste="onlyNumber(this)
function onlyNumber(o){
	if(o.value.length==1){
		// 清除"数字"和"."以外的字符
		o.value = o.value.replace(/[^\d]/g,"");
		o.value=o.value.replace(/([^1-9])(\.\d{0,2})/g,'')
	} else {
		o.value=o.value.replace(/\D/g,'')
	}
}
