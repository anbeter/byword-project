document.addEventListener(
    "DOMContentLoaded",
    function () {

        const rows =
            document.querySelectorAll(
                '.inline-related'
            );

        rows.forEach(row => {

            initializeRow(row);

        });

    }
);

function initializeRow(row) {

    const contentTypeSelect =
        row.querySelector(
            'select[name$="-content_type"]'
        );

    const objectIdInput =
        row.querySelector(
            'input[name$="-object_id"]'
        );

    if (
        !contentTypeSelect ||
        !objectIdInput
    ) {
        return;
    }

    function loadObjects() {

        const pathParts =
            window.location.pathname.split('/');

        const activityId =
            pathParts[4];

        const contentTypeId =
            contentTypeSelect.value;

        if (!contentTypeId) {
            return;
        }

        fetch(
            `/admin/byword/activity/load-content-objects/?activity_id=${activityId}&content_type_id=${contentTypeId}`
        )
        .then(response => response.json())
        .then(data => {

            let select =
                row.querySelector(
                    '.dynamic-object-select'
                );

            if (!select) {

                select =
                    document.createElement(
                        'select'
                    );

                select.classList.add(
                    'dynamic-object-select'
                );

                objectIdInput.parentNode.appendChild(
                    select
                );

                objectIdInput.style.display =
                    'none';
            }

            select.innerHTML = '';

            const allOption =
                document.createElement(
                    'option'
                );

            allOption.value = '';

            allOption.text = 'ALL';

            select.appendChild(
                allOption
            );

            data.forEach(item => {

                const option =
                    document.createElement(
                        'option'
                    );

                option.value =
                    item.id;

                option.text =
                    item.text;

                if (
                    String(item.id) ===
                    String(objectIdInput.value)
                ) {
                    option.selected = true;
                }

                select.appendChild(
                    option
                );

            });

            select.addEventListener(
                'change',
                function () {

                    objectIdInput.value =
                        this.value;

                }
            );

        });

    }

    contentTypeSelect.addEventListener(
        'change',
        loadObjects
    );

    // 🔥 carrega automaticamente
    loadObjects();
}

/*document.addEventListener(
    "DOMContentLoaded",
    function () {

        const rows =
            document.querySelectorAll(
                '.inline-related'
            );

        rows.forEach(row => {

            const contentTypeSelect =
                row.querySelector(
                    'select[name$="-content_type"]'
                );

            const objectIdInput =
                row.querySelector(
                    'input[name$="-object_id"]'
                );

            if (
                !contentTypeSelect ||
                !objectIdInput
            ) {
                return;
            }

            contentTypeSelect.addEventListener(
                'change',
                function () {

                    const pathParts =
                        window.location.pathname.split('/');

                    const activityId =
                        pathParts[4];

                    const contentTypeId =
                        this.value;

                    fetch(
                        `/admin/byword/activity/load-content-objects/?activity_id=${activityId}&content_type_id=${contentTypeId}`
                    )
                    .then(response => response.json())
                    .then(data => {

                        let select =
                            row.querySelector(
                                '.dynamic-object-select'
                            );

                        if (!select) {

                            select =
                                document.createElement(
                                    'select'
                                );

                            select.classList.add(
                                'dynamic-object-select'
                            );

                            objectIdInput.parentNode.appendChild(
                                select
                            );

                            objectIdInput.style.display =
                                'none';
                        }

                        select.innerHTML = '';

                        const allOption =
                            document.createElement(
                                'option'
                            );

                        allOption.value = '';

                        allOption.text =
                            'ALL';

                        select.appendChild(
                            allOption
                        );

                        data.forEach(item => {

                            const option =
                                document.createElement(
                                    'option'
                                );

                            option.value =
                                item.id;

                            option.text =
                                item.text;

                            select.appendChild(
                                option
                            );

                        });

                        select.addEventListener(
                            'change',
                            function () {

                                objectIdInput.value =
                                    this.value;

                            }
                        );

                    });

                }
            );

        });

    }
);*/
