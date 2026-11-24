---
layout: default
---

# ExSce Metamodels

<div class="version-selector" markdown="0">
<label for="release">Version</label>
<select id="release" onchange="window.location.href=this.value">
<option value="{{ '/latest/' | relative_url }}" {% if page.release == 'latest' %}selected{% endif %}>Latest (main)</option>
{% if site.data.releases.versions.size > 0 %}
<option value="{{ '/stable/' | relative_url }}" {% if page.release == 'stable' %}selected{% endif %}>Stable ({{ site.data.releases.versions.first }})</option>
{% endif %}
{% for version in site.data.releases.versions %}
<option value="{{ '/' | append: version | append: '/' | relative_url }}" {% if page.release == version %}selected{% endif %}>{{ version }}</option>
{% endfor %}
</select>
</div>

In the below table are all the models created during the development
of the ExSce Workbench. They are referred to from the various tutorials
listed on the
[Repository of Executable Scenarios](https://sesame-project.github.io/exsce/exsce-repo.html).

<table id="models" class="table table-striped" style="width:100%;white-space:nowrap;">
<thead>
<tr>
<th>Filename</th>
<th>Extension</th>
<th style="display:none"></th>
</tr>
</thead>
<tbody>
{% for item in site.data.releases.listings[page.release]%}
{% for file_data in item[1] %}
<tr>
<td>
  <a href="{{ file_data.path }}">{{ file_data.name }}</a>
</td>
<td>
  {{ file_data.extension }}
</td>
<td style="display:none">
{{ item[0]  }}
</td>
</tr>
{% endfor %}
{% endfor %}
</tbody>
</table>

<script src="{{ "/assets/js/jquery-3.5.1.min.js" | relative_url }}"></script>
<script src="{{ "/assets/js/jquery.dataTables.min.js" | relative_url }}"></script>
<script src="{{ "/assets/js/dataTables.bootstrap5.min.js" | relative_url }}"></script>
<script src="{{ "/assets/js/dataTables.rowGroup.min.js" | relative_url }}"></script>
<script>
new DataTable('#models', {
  scrollX: true,
  order: [[2, 'asc']],
  rowGroup: {
    dataSrc: 2
  },
  pageLength: 25
});
</script>
