from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from .models import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import serializers
from django.views.generic import CreateView
from .forms import ContactForm


class IndexPage(TemplateView):
    def get(self, request, **kwargs):
        article_data = []
        all_articles = Article.objects.all().order_by('-created_at')[:9]

        for article in all_articles:
            article_data.append({
                'title': article.title,
                'cover': article.cover,
                'category': article.category,
                'created_at': article.created_at.date(),
            })

        promote_data = []
        all_promote_article = Article.objects.filter(promote=True)
        for promote_article in all_promote_article:
            promote_data.append({
                'category': promote_article.category.title,
                'title': promote_article.title,
                'cover': promote_article.cover,
                'author': promote_article.author.user.first_name + " " + promote_article.author.user.last_name,
                'avatar': promote_article.author.avatar.url if promote_article.author.avatar else None,
                'created_at': promote_article.created_at.date(),
            })
        context = {
            'article_data': article_data,
            'promote_article_data': promote_data,
        }

        return render(request, 'index.html', context)


# class ContactPage(TemplateView):
#     template_name = "contactus.html"

class ContactPage(CreateView):
    model = Contactus
    form_class = ContactForm
    success_url = reverse_lazy("thanks")
    template_name = "contactus.html"


def thanks(request):
    from django.http import HttpResponse
    return HttpResponse("Thank you! Will get in touch soon.")


class AllArticleAPIView(APIView):
    def get(self, request, format=None):
        try:
            all_articles = Article.objects.all().order_by('created_at')[:20]
            data = []

            for article in all_articles:
                data.append({
                    "title": article.title,
                    "cover": article.cover.url if article.cover else None,
                    "content": article.content,
                    "created_at": article.created_at,
                    "category": article.category.title,
                    "author": article.author.user.first_name + " " + article.author.user.last_name,
                    "promote": article.promote,
                })

            return Response({'data': data}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server Error, We'll Check It Later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SingleArticleAPIView(APIView):
    def get(self, request, format=None):
        try:
            article_title = request.GET['article_title']
            article = Article.objects.filter(title__contains=article_title)
            serialized_data = serializers.SingleArticleSerializer(article, many=True)
            data = serialized_data.data

            return Response({'data': data}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server Error, We'll Check It Later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchArticleAPIView(APIView):

    def get(self, request, format=None):
        try:
            from django.db.models import Q

            query = request.GET['query']
            articles = Article.objects.filter(Q(content__icontains=query))
            data = []

            for article in articles:
                data.append({
                    "title": article.title,
                    "cover": article.cover.url if article.cover else None,
                    "content": article.content,
                    "created_at": article.created_at,
                    "category": article.category.title,
                    "author": article.author.user.first_name + ' ' + article.author.user.last_name,
                    "promote": article.promote,
                })

            return Response({'data': data}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server Error, We'll Check It Later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SubmitArticleAPIView(APIView):

    def post(self, request, format=None):

        try:
            serializer = serializers.SubmitArticleSerializer(data=request.data)
            if serializer.is_valid():
                title = serializer.data.get('title')
                cover = request.FILES['cover']
                content = serializer.data.get('content')
                category_id = serializer.data.get('category_id')
                author_id = serializer.data.get('author_id')
                meta_description = serializer.data.get('meta_description')
                meta_keywords = serializer.data.get('meta_keywords')
                promote = serializer.data.get('promote')
            else:
                return Response({'status': 'Bad Request.'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=author_id)
            author = UserProfile.objects.get(user=user)
            category = Category.objects.get(id=category_id)

            article = Article()
            article.title = title
            article.cover = cover
            article.content = content
            article.category = category
            article.author = author
            article.meta_description = meta_description
            article.meta_keywords = meta_keywords
            article.promote = promote
            article.save()

            return Response({'status': 'OK'}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server Error, We'll Check It Later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateArticleAPIView(APIView):

    def post(self, request, format=None):
        try:
            serializer = serializers.UpdateArticleCoverSerializer(data=request.data)

            if serializer.is_valid():
                article_id = serializer.data.get('article_id')
                cover = request.FILES['cover']
            else:
                return Response({'status': 'Bad Request.'}, status=status.HTTP_400_BAD_REQUEST)

            with open('files/article_cover/' + cover.name, 'wb+') as destination:
                for chunk in cover.chunks():
                    destination.write(chunk)

            # upload file in directory
            cover_url = 'files/article_cover/' + cover.name

            # delete file source
            # import os
            # os.remove('files/article_cover/' + 'HD Beautiful Nature Wallpaper 010.jpg')

            # change file path + name in database
            Article.objects.filter(id=article_id).update(cover=cover_url)

            return Response({'status': 'OK'}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server Error, We'll Check It Later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeleteArticleAPIView(APIView):

    def post(self, request, format=None):
        try:
            serializer = serializers.DeleteArticleSerializer(data=request.data)

            if serializer.is_valid():
                article_id = serializer.data.get('article_id')
            else:
                return Response({'status': 'Bad Request.'}, status=status.HTTP_400_BAD_REQUEST)

            Article.objects.filter(id=article_id).delete()

            return Response({'status': 'OK'}, status=status.HTTP_200_OK)

        except:
            return Response({'status': "Internal Server Error, We'll Check It Later"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
