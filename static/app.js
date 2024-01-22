$(document).ready(function () {
    $("#uploadButton").click(function () {
        // Membuat objek FormData dan menambahkan data formulir
        let formData = new FormData();
        formData.append('nama', $('#namaUpload').val());
        formData.append('file', $('#file')[0].files[0]);

        // Ganti URL_API dengan URL API yang sesuai dengan backend Anda
        let apiUrl = "upload";

        // Kirim data formulir ke API menggunakan jQuery AJAX
        $.ajax({
            type: "POST",
            url: apiUrl,
            data: formData,
            contentType: false,
            processData: false,
            success: function (data) {
                // Tanggapan dari API
                if (data) {
                    // Menampilkan modal
                    $("#VideoModal").modal("show");

                    // Mengisi konten modal dengan data dari respons server
                    $("#iframeVideo").attr("href", `http://127.0.0.1:5000/video_feed_upload?file_path=${data.file_path}&nama=${data.nama}`);
                } else {
                    // Jika ada kesalahan, tampilkan pesan kesalahan
                    alert("Gagal mengupload video.");
                }
            },
            error: function (xhr, status, error) {
                // Tanggapan error dari API
                console.error("Error:", xhr, status, error);
                alert("Terjadi kesalahan. Silakan coba lagi.");
            }
        });
    });
    $("#realtimeButton").click(function () {
        // Membuat objek FormData dan menambahkan data formulir
        let data = {
            'nama': $('#namaRealtime').val(),
            'waktu': $('#waktu').val(),
        };

        if (data) {
            // Menampilkan modal
            $("#VideoModal").modal("show");

            // Mengisi konten modal dengan data dari respons server
            $("#iframeVideo").attr("href", `http://127.0.0.1:5000/video_feed_realtime?nama=${data.nama}&waktu=${data.waktu}`);
        } else {
            // Jika ada kesalahan, tampilkan pesan kesalahan
            alert("Gagal mengupload video.");
        }
    });
});
