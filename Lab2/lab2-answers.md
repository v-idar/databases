
Question to answer:
1. Which relations have natural keys?
Imdb_key might be a natural key?
User_name is also natural  
And theater_name.
2. Is there a risk that any of the natural keys will ever change?
The Imdb key i guess can change, same if we were to declare title and year as a separate key.
3. Are there any weak entity sets?
Yes, the screening entity set is weak since it does not have its own.
4. In which relations do you want to use an invented key. Why?
I want to use a synthetic key for ticket_id.  Because it has to be a generated number which is unique..?


[comment]: <> (Det här är ett exempel på students)
[comment]: <> (students(_s_id_, s_name, gpa, size_hs))
[comment]: <> (colleges(_c_name_, state, enrollment))
[comment]: <> (applications(/_s_id_/, /_c_name_/, _major_, decision))


theaters(_theater_name_, capacite)
movies(_imdb_key_, movie_title, production_year, running_time)
screenings(/_theater_name_/, /_imdb_key_/, /_ticket_id/, start_time)
ticket(_ticket_id_)
customer(_user_name_, /_ticket_id_/, full_name, password)

7. Det finns två sätt att hålla reda på hur många lediga platser det finns till en föreställning. Beskriv båda.
7. Svar: capacity minus tickets 