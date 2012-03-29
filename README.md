#Django Kendo UI backend

##Description

Provides a generic view that will feed Kendo UI (http://kendoui.com) components with model data. Supports server-side pagin, filtering, sorting and grouping. 

##Requirements 

* Django >=1.3.0
* json_utils >=0.2
* querystring_parser>=1.1


##Installation

    $ pip install django-kendoui-backend

or

    $ easy_install django-kendoui-backend

or (reqiuires you to solve dependencies first)

    $ git clone git://github.com/omab/django-kendoui-backend.git
    $ export PYTHONPATH=$PYTHONPATH:$(pwd)/django-kendoui-backend/


or (reqiuires you to solve dependencies first)

    $ git clone git://github.com/omab/django-kendoui-backend.git
    $ cd django-kendoui-backend
    $ sudo python setup.py install

## Usage

* Add to urls.py:
    
        from kendoui_backend.views import KendoListProviderView
        url(r'^example_model$', KendoListProviderView.as_view(model=ExampleModel), name='example_model'),
    

* Feed your Kendo UI component with data source, e.g.:

    
        var ds = new kendo.data.DataSource({
            pageSize: 20,
            serverPaging: true,
            serverFiltering: true,
            serverSorting: true,
            transport: {
                read: {
                    url: "{% url example_model %}",
                    dataType: "json",
                }
            },
            schema: {
                total: "count",
                data: function(d) {return d['payload'].map(function(e) {return e['fields']})} // This bit is required for Kendo UI to navigate through data set received from the server correctly
            }
        }
    

* Create a Kendo UI component with a DataSource created in above step:
    
    
        $("#dropdown").kendoDropDownList({
            dataTextField: "name",
            dataValueField: "number",
            dataSource: ds3,
            index: 0,
        });
    


For more details see the example app

## License
This code is released under MIT License.

