from django.urls import path

from .views import (
    # Course views
    CourseListView,
    CourseDetailView,
    CourseCreateView,
    CourseUpdateView,
    CourseDeleteView,
    # Group views
    GroupListView,
    GroupDetailView,
    GroupCreateView,
    GroupUpdateView,
    GroupDeleteView,
    # Student management
    add_students_to_group,
    remove_student_from_group,
    change_group_teacher,
    assign_user_to_groups,
    # Certificate & coins views
    certificate_list,
    certificate_upload,
    student_certificates,
    student_coins,
    # Market views
    student_market,
    buy_product,
    MarketProductListView,
    MarketProductCreateView,
    MarketProductUpdateView,
    MarketProductDeleteView,
    MarketPurchaseListView,
    confirm_purchase,
)

urlpatterns = [
    # Courses
    path("courses/", CourseListView.as_view(), name="course_list"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course_detail"),
    path("courses/create/", CourseCreateView.as_view(), name="course_create"),
    path("courses/<int:pk>/edit/", CourseUpdateView.as_view(), name="course_update"),
    path("courses/<int:pk>/delete/", CourseDeleteView.as_view(), name="course_delete"),
    # Groups
    path("groups/", GroupListView.as_view(), name="group_list"),
    path("groups/<int:pk>/", GroupDetailView.as_view(), name="group_detail"),
    path("groups/create/", GroupCreateView.as_view(), name="group_create"),
    path("groups/<int:pk>/edit/", GroupUpdateView.as_view(), name="group_update"),
    path("groups/<int:pk>/delete/", GroupDeleteView.as_view(), name="group_delete"),
    # Student management
    path(
        "groups/<int:group_id>/add-students/",
        add_students_to_group,
        name="add_students_to_group",
    ),
    path(
        "groups/<int:group_id>/remove-student/<int:student_id>/",
        remove_student_from_group,
        name="remove_student_from_group",
    ),
    path(
        "groups/<int:group_id>/change-teacher/",
        change_group_teacher,
        name="change_group_teacher",
    ),
    path(
        "users/<int:user_id>/assign-groups/",
        assign_user_to_groups,
        name="assign_user_to_groups",
    ),
    # Certificates + "Mening sertifikatlarim / tangalarim"
    path("certificates/", certificate_list, name="certificate_list"),
    path(
        "certificates/upload/<int:student_id>/",
        certificate_upload,
        name="certificate_upload",
    ),
    path("my-certificates/", student_certificates, name="student_certificates"),
    path("my-coins/", student_coins, name="student_coins"),
    # Market (student)
    path("market/", student_market, name="student_market"),
    path("market/buy/<int:product_id>/", buy_product, name="buy_product"),
    # Market (admin)
    path(
        "market/admin/products/",
        MarketProductListView.as_view(),
        name="market_product_list",
    ),
    path(
        "market/admin/products/create/",
        MarketProductCreateView.as_view(),
        name="market_product_create",
    ),
    path(
        "market/admin/products/<int:pk>/edit/",
        MarketProductUpdateView.as_view(),
        name="market_product_update",
    ),
    path(
        "market/admin/products/<int:pk>/delete/",
        MarketProductDeleteView.as_view(),
        name="market_product_delete",
    ),
    path(
        "market/admin/purchases/",
        MarketPurchaseListView.as_view(),
        name="market_purchase_list",
    ),
    path(
        "market/admin/purchases/<int:pk>/confirm/",
        confirm_purchase,
        name="market_purchase_confirm",
    ),
]
