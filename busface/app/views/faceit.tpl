% rebase('base.tpl', title='face', path=path)
<div class="container">
%#generate list of rows of items
% i = 1
%for item in items:
<form id="form-{{i}}" action="/face/{{fanhao}}?page={{page}}&like={{like}}" method="post">
	<div class="row py-3">
		<div class="col-12 col-md-4">
		<img class="img-fluid img-thumbnail" src={{item['url']}}>
		</div>
			<div class="col-7 col-md-5">
			<img src="data:;base64,{{ item['image'] }}"/>
			<input type=hidden name="faceid" value="{{item['id']}}">
		    <button type="submit" name="submit" class="btn btn-danger btn-sm" value="0">不喜欢</button>
			</div>
		</div>
		<div class="col-5 col-md-3  align-self-center">
		<input type=hidden name="formid" value="form-{{i}}">
		</div>

	</div>
	</form>
% i = i + 1
%end

<a class="nav-link" href="/tagit?page={{page}}&like={{like}}">return</a>
</div>