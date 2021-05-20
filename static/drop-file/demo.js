function showModal() {  //打开上传框
	var modal = document.getElementById('modal');
	var overlay = document.getElementsByClassName('overlay')[0];
	overlay.style.display = 'block';
	modal.style.display = 'block';
}
function closeModal() {  //关闭上传框
	var modal = document.getElementById('modal');
	var overlay = document.getElementsByClassName('overlay')[0];
	overlay.style.display = 'none';
	modal.style.display = 'none';
}


//用DOM2级方法为右上角的叉号和黑色遮罩层添加事件：点击后关闭上传框
document.getElementsByClassName('overlay')[0].addEventListener('click', closeModal, false);
document.getElementById('close').addEventListener('click', closeModal, false);

//利用html5 FormData() API,创建一个接收文件的对象，因为可以多次拖拽，这里采用单例模式创建对象Dragfiles
var Dragfiles=(function (){
	var instance;
	return function(){
		if(!instance){
			instance = new FormData();
		}
		return instance;
	}
}());
//为Dragfiles添加一个清空所有文件的方法
FormData.prototype.deleteAll=function () {
	var _this=this;
	this.forEach(function(value,key){
		_this.delete(key);
	})
}

//添加拖拽事件
var dz = document.getElementById('content');
dz.ondragover = function (ev) {
	//阻止浏览器默认打开文件的操作
	ev.preventDefault();
	//拖入文件后边框颜色变红
	this.style.borderColor = 'red';
}

dz.ondragleave = function () {
	//恢复边框颜色
	this.style.borderColor = 'gray';
}
dz.ondrop = function (ev) {
	var oldlen = this.childNodes[1].childNodes[1].childNodes.length;
	var send_type = $('#send_type').val()  //需要发送的文件类型
	// 如果文件类型是OP FORM 则一次可以传最多20个文件，否则只能传一个文件
	var max_files = 1  //限制一次上传文件的数量
	if (send_type === 'OP Form'){
		max_files = 20
	}
	// 如果文件类型是 Paperwork 则只能接受PDF
	var file_type = ['xls','xlsx'];   //限制文件扩展名
	if (send_type === 'Paperwork'){
		file_type = ['pdf']
	}
	if (send_type === 'Breakdown'){
		file_type = ['xls','xlsx', 'xlsm', 'pdf']
	}
	if (send_type === 'Parcel List'){
		file_type = ['pdf']
	}
	if (send_type === 'Delivery POD'){
		file_type = ['pdf']
	}
	console.log()
	var max_size = 5000  //限制一次上传文件的大小 5000KB = 5M
	if (oldlen >= max_files) {
		alert('one times only ' + max_files + ' files can be uploading...');
		return;
	}
	//恢复边框颜色
	this.style.borderColor = 'gray';
	//阻止浏览器默认打开文件的操作
	ev.preventDefault();
	var files = ev.dataTransfer.files;
	var len=files.length,
		i=0;
	var frag=document.createDocumentFragment();  //为了减少js修改dom树的频度，先创建一个fragment，然后在fragment里操作
	var tr,time,size;
	var newForm=Dragfiles(); //获取单例
	var it=newForm.entries(); //创建一个迭代器，测试用
	var k = 0;
	if (len + oldlen > max_files) len = max_files - oldlen;
	console.log('file_type = ' + file_type )
	console.log('max_files == ' + max_files)
	console.log('send_type == ' + send_type)
	while(k<len){
		// 获取文件名
		let filename = files[i].name;
		let extension = filename.split('.').pop().toLowerCase();  //jpg
		//获取文件大小
		size=Math.round(files[i].size * 100 / 1024) / 100 + 'KB';
		//获取格式化的修改时间
		time = files[i].lastModifiedDate.toLocaleDateString() + ' '+files[i].lastModifiedDate.toTimeString().split(' ')[0];
   	    console.log(size+' '+time);
		if (file_type.indexOf(extension)>=0)
		{
			tr=document.createElement('tr');
			tr.innerHTML='<td>'+files[i].name+'</td><td>'+size+'</td><td>DELETE</td>';
			frag.appendChild(tr);
			//添加文件到newForm
			newForm.append(files[i].name,files[i]);
			//console.log(it.next());
			k++;
		}
		i++;
	}
	newForm.append('ref_no',$('#ref').val());
	newForm.append('send_type',send_type);

	this.childNodes[1].childNodes[1].appendChild(frag);
	//为什么是‘1’？文档里几乎每一样东西都是一个节点，甚至连空格和换行符都会被解释成节点。而且都包含在childNodes属性所返回的数组中.不同于jade模板
}
function blink()
{
  document.getElementById('content').style.borderColor = 'gray';
}

//ajax上传文件
function upload(){
	if(document.getElementsByTagName('tbody')[1].hasChildNodes()==false){
		document.getElementById('content').style.borderColor = 'red';
		setTimeout(blink,200);
		return false;
	}
	var data=Dragfiles(); //获取formData
	$.ajax({
		url: '/slot/uploads/',
		type: 'POST',
		data: data,
		async: true,
		cache: false,
		contentType: false,
		processData: false,
		success: function () {
			// alert('Files uploading succeed!')
			closeModal();
			data.deleteAll(); //清空formData
			$('.tbody').empty(); //清空列表
			window.location.reload();
		},
		error: function (returndata) {
			alert('Files uploading failed!')
		}
	});
}
// 用事件委托的方法为‘删除’添加点击事件，使用jquery中的on方法
$(".tbody").on('click','tr td:last-child',function(){
	//删除拖拽框已有的文件
	var temp=Dragfiles();
	var key=$(this).prev().prev().prev().text();
	console.log(key);
	temp.delete(key);
	$(this).parent().remove();
});
//清空所有内容
function clearAll(){
	if(document.getElementsByTagName('tbody')[1].hasChildNodes()==false){
		document.getElementById('content').style.borderColor = 'red';
		setTimeout(blink,300);
		return false;
	}
	var data=Dragfiles(); 
	data.deleteAll(); //清空formData
	//$('.tbody').empty(); 等同于以下方法
	document.getElementsByTagName('tbody')[1].innerHTML='';
}