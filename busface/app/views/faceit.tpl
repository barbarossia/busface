% rebase('base.tpl', title='face', path=path)
% curr_page = page_info[2]
<div class="container">
%#generate list of rows of items
% i = 1
%for item in items:
<form id="form-{{i}}" action="/faceit/{{item.fanhao}}?page={{curr_page}}&like={{like}}" method="post">
	<div class="row py-3">
		<div class="col-12 col-md-4">
		<img class="img-fluid img-thumbnail coverimg" src={{item.cover_img_url}}>
		</div>

			<div class="col-7 col-md-5">
			<div class="small text-muted">id: {{item.id}}</div>
			<h6>{{item.fanhao}} </h6>
			<a href="{{item.url}}" target="_blank"> {{item.title[:30]}} </a>
			<div>
			% for face in item.faces_dict:
			<input type=hidden name="faceid" value="{{face.id}}">
			<span class="badge badge-primary">{{face.url}}</span>
			% if like is None or like == 1:
		    <button type="submit" name="submit" class="btn btn-danger btn-sm" value="0">不喜欢</button>
            % end
			% end
			</div>
		</div>
		<div class="col-5 col-md-3  align-self-center">
		<input type=hidden name="formid" value="form-{{i}}">
		</div>
	</div>
	</form>
% i = i + 1
%end
% include('pagination.tpl', page_info=page_info)

</div>