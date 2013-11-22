============
pyramid_skue
============

``pyramid_skue`` is a library for builidn REST API services on top of `Pyramid`_ framework.

.. _`Pyramid`: http://www.pylonsproject.org/


Installation
------------
Requires Pyramid >= 1.5a2

Install with pip::

    pip install pyramid_skue

or using ``easy_install``::

    easy_install pyramid_skue


Usage
-----

Create ``api`` python package inside your main project package.

Populate ``api/resourses.py`` with the defenition of resource::

    from pyramid_skue.rest.api import ResourceDescription
    from pyramid_skue.rest.api import HttpMethodDescription
    from pyramid_skue.rest.api import HttpParameterDescription
    from pyramid_skue.http import CommonResponse
    from pyramid_skue.rest.resources import DocumentResource
    from .response import MessageResourceJson

    class MessageResource(DocumentResource):
        """Represents resource for readin/creating messages."""

        # Resource definition
        def describe_resource(self):
            """Self description.

            """
            description = 'Author of the message'
            author_param = HttpParameterDescription(
                'author', 'string', is_required=True,
                description=description)

            description = 'Title of the message'
            title_param = HttpParameterDescription(
                'title', 'string', is_required=True,
                description=description)

            description = 'Title of the message (optional)'
            title_optional_param = HttpParameterDescription(
                'title', 'string', is_required=False,
                description=description)

            description = 'Message body'
            body_param = HttpParameterDescription(
                'body', 'string', is_required=True,
                description=description)

            description = "Get existing messages"
            get_method = HttpMethodDescription(
                'GET', parameters=[title_optional_param],
                description=description)

            description = "Post message"
            post_method = HttpMethodDescription(
                'POST', parameters=[author_param, title_param, body_param],
                description=description)

            description = "Create/Get messages"
            resource = ResourceDescription(
                'MessageResource', url="/api/message",
                methods=[get_method, post_method],
                description=description)
            return resource

        def read_resource(self):
            """
            Return messages. Can be filtered by title.
            Assuming that ``storage`` is some database you're using.

            """
            title = self.payload.get('title')
            if title:
                messages = storage.filter(title).all()
            else:
                messages = storage.all()

            body = MessageResourceJson(messages)
            return CommonResponse.success(body)

        def create_resource(self):
            """Create message.

            ``storage`` is some hypothetical database.

            """
            author = self.payload.get('author')
            title = self.payload.get('title')
            body = self.payload.get('body')

            message_id = storage.create_message(author=author, title=title, body=body)
            resource_uri = self.get_resoruce_uri(message_id)

            return CommonResponse.resource_created(resource_uri)

Then add ``api/response.py``::
  
    from pyramid_skue.json.utils import ResourceJSONRepresentation

    class MessageResourceJson(ResourceJSONRepresentation):
        """Represents a JSON response for MessageResource."""
        def __init__(self, messages):
            ResourceJSONRepresentation.__init__(self, 'MessageResource')

            self.objects = []

            for message in messages:
                self.objects.append({
                    'author': message.author,
                    'title': message.title,
                    'body': message.body})

Now register the views in your ``__init__.py``::

    config.add_route('api-message', '/api/message')
    config.add_view('your_app.api.resources.MessageResource',
                    route_name='api-message',
                    renderer='string',
                    permission='view',  # whatever permission you like
                    check_csrf=True)

It's better to secure your views agains CSRF attacs, look at the `pyramid's documentation`_.

.. _`pyramid's documentation`: http://docs.pylonsproject.org/projects/pyramid/en/1.5-branch/narr/sessions.html#preventing-cross-site-request-forgery-attacks

Contacts
--------
The project is maintained by Cyril Panshine (`@CyrilPanshine`_). Bug reports and pull requests are very much welcomed!

.. _`@CyrilPanshine`: https://twitter.com/CyrilPanshine
