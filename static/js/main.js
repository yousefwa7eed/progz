$(document).ready(function() {
    $('.datatable').each(function() {
        if ($(this).data('paginate') === 'server') return;
        if (!$.fn.DataTable.isDataTable(this)) {
            $(this).DataTable({
                language: {
                    url: 'https://cdn.datatables.net/plug-ins/1.13.11/i18n/ar.json',
                    emptyTable: 'لا توجد بيانات'
                },
                responsive: true,
                pageLength: 25,
                ordering: true,
                paging: $(this).data('client-paginate') !== false,
                info: $(this).data('client-paginate') !== false,
            });
        }
    });

    $('.select2').select2({
        theme: 'bootstrap-5',
        width: '100%',
        dir: 'rtl'
    });

    $('.auto-submit').on('change', function() {
        $(this).closest('form').submit();
    });

    // Auto search with debounce
    var searchTimer;
    $('.auto-search').on('input', function() {
        var $input = $(this);
        var $form = $input.closest('form');
        clearTimeout(searchTimer);
        $input.closest('.input-group').find('.search-clear').toggleClass('d-none', !$input.val().length);
        searchTimer = setTimeout(function() {
            $form.submit();
        }, 300);
    });

    // Search clear button
    $(document).on('click', '.search-clear', function() {
        var $input = $(this).closest('.input-group').find('.auto-search');
        $input.val('');
        $(this).addClass('d-none');
        $input.closest('form').submit();
    });

    // Init clear button visibility
    $('.auto-search').each(function() {
        $(this).closest('.input-group').find('.search-clear').toggleClass('d-none', !$(this).val().length);
    });

    // Navbar dropdown arrow animation
    $(document).on('click', '.navbar .dropdown [data-bs-toggle="dropdown"]', function() {
        var $arrow = $(this).find('.dropdown-arrow');
        var $dropdown = $(this).parent();
        setTimeout(function() {
            $arrow.toggleClass('rotated', $dropdown.hasClass('show'));
        }, 100);
    });

    $('#select-all').on('change', function() {
        $('.select-item').prop('checked', $(this).prop('checked'));
    });

    setTimeout(function() {
        $('.alert-dismissible').fadeOut('slow');
    }, 5000);
});
