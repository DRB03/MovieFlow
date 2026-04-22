from django import forms

class MovieCommentForm(forms.Form):
    review= forms.CharField(label="Reseña", min_length=5 ,required=True,
                             widget =  forms.Textarea(attrs={"class": "block w-full rounded-md bg-white px-3" 
                                  "py-1.5 text-base text-gray-900 outline outline-1"
                                  "-outline-offset-1 outline-gray-300 placeholder:text-gray-400" 
                                  "focus:outline focus:outline-2 focus:-outline-offset-2" 
                                  "focus:outline-indigo-600 sm:text-sm/6"}) )

class MovieReviewForm(forms.Form):
    # CAMBIO: max_value modificado a 10
    rating = forms.IntegerField(label="Calificación (1-10)", min_value=1, max_value=10, required=True)
    
    review = forms.CharField(label="Reseña", min_length=20, required=True, 
                             widget=forms.Textarea(attrs={
                                 "class": "block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6",
                                 "rows": "4"
                             })) 
    title = forms.CharField(label="Titulo", required=True)
    
    title.widget.attrs.update({
        "class": "block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6"
    })
    rating.widget.attrs.update({
        "class": "rounded-md bg-white py-1.5 pl-3 pr-2 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6",
        "placeholder": "1 al 10"
    })