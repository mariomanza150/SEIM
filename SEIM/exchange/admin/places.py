from django.contrib import admin
from ..models.places import Campus, City, Country, State, University, Institution
from ..models.places.address import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'line_1',
        'line_2',
        'postal_code',
        'city',
        'state',
        'country',
    )

    list_filter = (
        'country',
        'state',
        'city',
    )

    search_fields = (
        'line_1',
        'line_2',
        'postal_code',
        'city__name',
        'state__name',
        'country__name',
    )

    autocomplete_fields = (
        'city',
        'state',
        'country',
    )


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'university',
        'get_city',
        'get_state',
        'get_country',
        'latitude',
        'longitude'
    )

    list_filter = (
        'address__country',
        'address__state',
        'address__city',
        'university',
    )

    search_fields = (
        'name',
        'university__name',
        'address__city__name',
        'address__state__name',
        'address__country__name',
    )

    autocomplete_fields = (
        'university',
        'address',
    )

    @admin.display(description='City')
    def get_city(self, obj):
        return obj.address.city.name if obj.address and obj.address.city else None

    @admin.display(description='State')
    def get_state(self, obj):
        return obj.address.state.name if obj.address and obj.address.state else None

    @admin.display(description='Country')
    def get_country(self, obj):
        return obj.address.country.name if obj.address and obj.address.country else None


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'country')
    search_fields = ('name', 'state', 'country')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'phone_code')
    search_fields = ('name', 'code')


# Optional: If you have a `State` model not shown above
@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'code')
    search_fields = ('name', 'country', 'code')


# Optional: If University is not yet registered
@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'university', 'campus', 'main_contact')
    search_fields = (
        'name',
        'university__name',
        'campus__name',
        'main_contact__full_name',  # Adjust if `ContactProfile` uses a different field
    )
    autocomplete_fields = ('main_contact', 'campus', 'university')
    list_filter = ('university', 'campus')
