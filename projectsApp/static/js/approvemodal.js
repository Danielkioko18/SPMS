$('#submit_approval').click(function() {
  var project_id = $('#project_id').val();
  var allocated_lecturer = $('#allocated_lecturer').val();
  var comment = $('#comment').val();

  $.ajax({
    url: '/approve_project/',
    type: 'POST',
    data: {
      'project_id': project_id,
      'allocated_lecturer': allocated_lecturer,
      'comment': comment
    },
    success: function(response) {
      alert('Project approved successfully!');
    },
    error: function(xhr, status, error) {
      alert('Error approving project: ' + error);
    }
  });
});