/** layuiAdmin.std-v1.0.0 LPPL License By http://www.layui.com/admin/ */ ;
layui.define(["table", "form"], function(e) {
	var t = layui.$,
		i = layui.table,
		$=layui.jquery;
	layui.form;
	console.log('forum.js loaded');
	i.render({
		elem: "#LAY-app-forum-list",
		url: "/get_job_list/",
		cols: [
			[{
				field: "id",
				title: "图书编号",
				width: 90,
				fixed: "left",
				align: "center",
			}, {
				field: "book_name",
				title: "书名"
			}, {
				field: "price",
				title: "价格(元)",
				width: 100
			}, {
				field: "rating",
				title: "评分",
				width: 80
			}, {
				field: "read_count",
				title: "阅读人数",
				width: 100
			}, {
				field: "comment_count",
				title: "评论数",
				width: 80
			},  {
				field: "author",
				title: "作者"
			},{	
				field: "publisher",
				title: "出版社",
				width: 150,
			},{	
				field: "category",
				title: "类型",
				width: 100,
				align: "left"
			},{	
				title: "操作",
				width: 130,
				align: "center",
				fixed: "right",
				toolbar: "#table-forum-list"
			}]
		],
		page: !0,
		limit: 15,
		limits: [15, 20, 30, 50],
		text: "对不起，加载出现异常！"
	}),  i.on("tool(LAY-app-forum-list)", function(e) {
		e.data;
		console.log(e.data.send_key)
		if("send" === e.event) layer.confirm("确定收藏图书 "+e.data.book_name+" 吗？", function(t) {
			$.ajax({
				   type: 'POST',
				   data:{"book_id":e.data.id, "send_key":e.data.send_key},
				   url: '/send_job/',
				   success: function (res) {
					   layer.msg(res.msg);location.reload()
				   },
				   error:function(response){
					   layer.msg(response.msg);
				   }
			   }),
				layer.close(t)
		});
		else if("send_1" === e.event) layer.confirm("确定取消收藏 "+e.data.book_name+" 吗？", function(t){
			$.ajax({
				   type: 'POST',
				   data:{"book_id":e.data.id, "send_key":e.data.send_key},
				   url: '/send_job/',
				   success: function (res) {
					   layer.msg(res.msg);location.reload()
				   },
				   error:function(response){
					   layer.msg(response.msg);
				   }
			   }),layer.close(t)
		});
	}),e("forum", {})
});
