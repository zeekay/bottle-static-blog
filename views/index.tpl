<h1>Welcome to my site!</h1>

<h2>My posts</h2>
  <ul>
    % for name, url in posts.items():
        <li><a href="{{url}}">{{name}}</a></li>
    % end
  </ul>
