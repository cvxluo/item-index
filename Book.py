
import discord


class Book (object) :

    def __init__ (self, chapters, title = "\a", description = '\a', color = 1, per_page = 10) :
        self.chapters = chapters
        self.title = title
        self.description = description
        self.color = color
        self.per_page = per_page
        self.page_number = 0


    def set_per_page(self, per_page) :
        self.per_page = per_page


    def one_page_forward(self) :
        self.page_number += 1 if (self.page_number + 1) * self.per_page < sum([len(x) for x in self.chapters.values()]) else 0

    def one_page_backward(self) :
        self.page_number -= 1 if self.page_number > 0 else 0


    def page_forward(self, num_pages_forward) :
        self.page_number += num_pages_forward if (self.page_number + num_pages_forward) * self.per_page < sum([len(x) for x in self.chapters.values()]) else 0

    def page_backward(self, num_pages_backward) :
        self.page_number -= num_pages_backward if self.page_number - num_pages_backward >= 0 else 0



    # TODO: currently crashes in edge cases at the end of the book because of indexing issues - fix
    def get_current_page(self) :
        embed = discord.Embed(title=self.title, description=self.description, color=self.color)

        PER_PAGE = self.per_page
        page_number = self.page_number

        index = 0
        start_display = PER_PAGE * page_number
        end_display = PER_PAGE * (page_number + 1)

        for chapter in self.chapters :

            chapter_content = self.chapters[chapter]

            # Find which chapter the page is on
            if index + len(chapter_content) < PER_PAGE * page_number :
                index += len(chapter_content)


            else :
                content = ""

                # Index is now in the chapter
                start = start_display - index if start_display - index > 0 else 0
                end = end_display - index if end_display - index < len(chapter_content) else len(chapter_content) - 1


                for i in range(start, end) :
                    content += str(chapter_content[i]) + '\n'

                embed.add_field(name = chapter, value = content, inline = False)

                if end_display - index < len(chapter_content) :
                    break

                index += len(chapter_content)


        embed.set_footer(text = "Page: " + str(self.page_number + 1) + "/" + str(round(sum([len(x) for x in self.chapters.values()]) / self.per_page) + 1))

        return embed
