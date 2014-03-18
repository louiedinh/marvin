(require 'org-publish)

(org-publish-projects        
 '(
   ("marvin-notes"
    :base-directory "~/Dropbox/Org/"
    :base-extension "dummy-extension"
    :publishing-directory "~/Dropbox/public_html/"
    :include ("goals.org" "todos.org" "projects.org" "index.org")
    :recursive t
    :publishing-function org-publish-org-to-html
    :headline-levels 4             ; Just the default for this project.
    :auto-preamble 
    )
   ("marvin-static"
    :base-directory "~/Dropbox/Org/static/"
    :base-extension "css\\|js\\|png\\|jpg\\|gif\\|pdf\\|mp3\\|ogg\\|swf"
    :publishing-directory "~/Dropbox/public_html/"
    :recursive t
    :publishing-function org-publish-attachment
	  )
   ))

