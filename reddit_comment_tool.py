#!/usr/bin/env python3
"""
Reddit Comment Tool - Find high-traffic threads and generate promotional comments.
"""
import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from reddit_scraper import RedditScraper
from comment_generator import CommentGenerator

console = Console()


def display_posts(posts: list):
    """Display posts in a formatted table."""
    if not posts:
        console.print("[yellow]No posts found with significant engagement.[/yellow]")
        return
    
    table = Table(title="Top Reddit Posts", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="cyan", no_wrap=False, max_width=50)
    table.add_column("Subreddit", style="green")
    table.add_column("Score", justify="right", style="yellow")
    table.add_column("Comments", justify="right", style="blue")
    table.add_column("Engagement", justify="right", style="bold")
    
    for idx, post in enumerate(posts, 1):
        table.add_row(
            str(idx),
            post["title"][:47] + "..." if len(post["title"]) > 50 else post["title"],
            post["subreddit"],
            str(post["score"]),
            str(post["comments"]),
            str(post["engagement_score"])
        )
    
    console.print(table)


def display_results(posts: list, comments_dict: dict):
    """Display formatted results ready for copy-paste."""
    console.print("\n[bold green]=" * 60)
    console.print("[bold green]READY TO COPY-PASTE[/bold green]")
    console.print("[bold green]=" * 60 + "\n")
    
    for post in posts:
        url = post["url"]
        if url not in comments_dict:
            continue
        
        # Post header
        console.print(Panel(
            f"[bold cyan]{post['title']}[/bold cyan]\n"
            f"[dim]r/{post['subreddit']} | {post['score']} upvotes | {post['comments']} comments[/dim]",
            title="Post",
            border_style="cyan"
        ))
        
        # URL
        console.print(f"[bold yellow]Link:[/bold yellow] {url}\n")
        
        # Comments
        for idx, comment in enumerate(comments_dict[url], 1):
            console.print(f"[bold green]Comment {idx}:[/bold green]")
            console.print(Panel(comment, border_style="green"))
            console.print()
        
        console.print("[dim]" + "-" * 60 + "[/dim]\n")


def main():
    parser = argparse.ArgumentParser(
        description="Reddit Comment Tool - Find high-traffic threads and generate promotional comments"
    )
    parser.add_argument(
        "keyword",
        help="Keyword to search for on Reddit"
    )
    parser.add_argument(
        "-n", "--number",
        type=int,
        default=5,
        help="Number of top posts to process (default: 5)"
    )
    parser.add_argument(
        "-c", "--comments",
        type=int,
        default=1,
        help="Number of comment variations per post (default: 1)"
    )
    parser.add_argument(
        "--promotion-target",
        help="What to promote (overrides .env setting)"
    )
    parser.add_argument(
        "--promotion-context",
        help="Context about what you're promoting (overrides .env setting)"
    )
    parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Only show posts, don't generate comments"
    )
    
    args = parser.parse_args()
    
    console.print("[bold blue]Reddit Comment Tool[/bold blue]\n")
    console.print(f"[dim]Searching for:[/dim] [yellow]{args.keyword}[/yellow]")
    console.print(f"[dim]Top posts:[/dim] [yellow]{args.number}[/yellow]\n")
    
    # Initialize scraper
    try:
        scraper = RedditScraper()
        console.print("[green]✓[/green] Reddit API connected")
    except Exception as e:
        console.print(f"[red]✗[/red] Error connecting to Reddit: {e}")
        sys.exit(1)
    
    # Search for posts
    console.print(f"[dim]Searching Reddit for '{args.keyword}'...[/dim]")
    try:
        posts = scraper.get_top_posts(args.keyword, top_n=args.number)
        console.print(f"[green]✓[/green] Found {len(posts)} high-traffic posts\n")
    except Exception as e:
        console.print(f"[red]✗[/red] Error searching Reddit: {e}")
        sys.exit(1)
    
    # Display posts
    display_posts(posts)
    
    if args.no_generate:
        console.print("\n[yellow]Skipping comment generation (--no-generate flag)[/yellow]")
        return
    
    # Generate comments
    if not posts:
        console.print("[yellow]No posts to generate comments for.[/yellow]")
        return
    
    try:
        generator = CommentGenerator()
        console.print(f"\n[dim]Generating {args.comments} comment(s) per post...[/dim]")
        comments_dict = generator.generate_multiple_comments(
            posts,
            count=args.comments,
            promotion_target=args.promotion_target,
            promotion_context=args.promotion_context
        )
        console.print(f"[green]✓[/green] Generated comments\n")
    except Exception as e:
        console.print(f"[red]✗[/red] Error generating comments: {e}")
        sys.exit(1)
    
    # Display results
    display_results(posts, comments_dict)


if __name__ == "__main__":
    main()

