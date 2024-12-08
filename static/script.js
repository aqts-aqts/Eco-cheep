$(document).ready(function() {
    $('#questForm').on('submit', function(event) {
        event.preventDefault();
        var userResponse = $('#response').val();
        $.ajax({
            url: "/get_context",
            method: "POST",
            data: { response: userResponse },
            success: function(data) {
                if (data.next_question) {
                    $('#question').text(data.next_question);
                    $('#response').val('');
                } else {
                    $('#questForm').hide();
                    $('#suggestions').show();
                    $('#suggestions-list').empty();
                    data.suggestions.forEach(function(suggestion) {
                        var suggestionText = `
                            <li>
                                <strong>Suggestion:</strong> ${suggestion[0]}<br>
                                <strong>EXP:</strong> ${suggestion[1]}<br>
                                <strong>Impact:</strong> ${suggestion[3]}
                                <button class="btn btn-success select-suggestion" data-suggestion-text="${suggestion[0]}" data-exp="${suggestion[1]}" data-proof-text="${suggestion[2]}">Select</button>
                            </li>`;
                        $('#suggestions-list').append(suggestionText);
                    });

                    $('#followUpForm').show();
                }
            }
        });
    });

    $('#followUpForm').on('submit', function(event) {
        event.preventDefault();
        var userResponse = $('#followUpResponse').val();
        $.ajax({
            url: "/change_suggestions",
            method: "POST",
            data: { response: userResponse },
            success: function(data) {
                $('#suggestions-list').empty();
                data.suggestions.forEach(function(suggestion) {
                    var suggestionText = `
                        <li>
                            <strong>Suggestion:</strong> ${suggestion[0]}<br>
                            <strong>EXP:</strong> ${suggestion[1]}<br>
                            <strong>Impact:</strong> ${suggestion[3]}
                            <button class="btn btn-success select-suggestion" data-suggestion-text="${suggestion[0]}" data-exp="${suggestion[1]}" data-proof-text="${suggestion[2]}">Select</button>
                        </li>`;
                    $('#suggestions-list').append(suggestionText);
                });
                $('#followUpResponse').val('');
            }
        });
    });

    $(document).on('click', '.select-suggestion', function() {
        var suggestionText = $(this).data('suggestion-text');
        var expValue = $(this).data('exp');
        var proofText = $(this).data('proof-text');
        $.ajax({
            url: "/select_suggestion",
            method: "POST",
            data: { suggestion: suggestionText, exp: expValue, proof: proofText },
            success: function(data) {
                alert("Suggestion added to your quests! Evidence required: " + data.proof);
                $('#addQuestModal').modal('hide');
            }
        });
    });

    $('#completeQuestModal').on('show.bs.modal', function() {
        $.ajax({
            url: "/get_quests",
            method: "GET",
            success: function(data) {
                $('#questDropdown').empty();
                data.quests.forEach(function(quest) {
                    $('#questDropdown').append(`<option value="${quest.proof}">${quest.description}</option>`);
                });
            }
        });
    });

    $('#completeQuestForm').on('submit', function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: "/complete_quest",
            method: "POST",
            data: formData,
            contentType: false,
            processData: false, 
            success: function (data) {
                if (data.status == 'complete') {
                    alert("Quest completed!");
                } else if (data.status == 'incomplete') {
                    alert("Quest not completed. Please provide correct evidence.");
                } else {
                    alert("Error processing. Please try again.");
                }
                $('#completeQuestModal').modal('hide');
            }
        });
    });
});