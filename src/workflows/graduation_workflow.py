from src.core.file_manager import FileManager
from src.tasks.article_generator import ArticleGenerator
from src.tasks.data_visualizer import DataVisualizer
from src.utils.image_generator import ImageGenerator
from src.tasks.link_collector import LinkCollector
from src.utils.dashscope_image_client import DashScopeImageClient


class GraduationWorkflow:
    def __init__(self) -> None:
        self.fm = FileManager("/Users/wy770/Apache")
        self.article_generator = ArticleGenerator()
        self.visualizer = DataVisualizer(self.fm)
        self.link_collector = LinkCollector(self.fm)
        
        # 初始化通义万相客户端（如果API Key存在）
        dashscope_client = None
        try:
            dashscope_client = DashScopeImageClient()
        except ValueError:
            print("警告: 未配置 DASHSCOPE_API_KEY，将使用手动生成方式")
        
        self.image_generator = ImageGenerator(dashscope_client=dashscope_client)

    def _replace_placeholders(self, content: str) -> str:
        community_chart = self.visualizer.generate_community_trend()
        release_chart = self.visualizer.generate_release_timeline()
        vote_chart = self.visualizer.generate_vote_distribution()

        # 使用相对路径（文章在 outputs/articles/，图片在 outputs/images/）
        community_chart_rel = "../images/community_trend.png"
        release_chart_rel = "../images/release_timeline.png"
        vote_chart_rel = "../images/vote_distribution.png"

        content = content.replace("[COMMUNITY_TREND_CHART]", f"![Community Trend]({community_chart_rel})")
        content = content.replace("[RELEASE_TIMELINE_CHART]", f"![Release Timeline]({release_chart_rel})")
        content = content.replace("[VOTE_DISTRIBUTION_CHART]", f"![Vote Distribution]({vote_chart_rel})")
        
        # 替换可能存在的绝对路径和旧路径
        content = content.replace("/Users/wy770/Apache/outputs/images/", "../images/")
        content = content.replace("outputs/images/", "../images/")
        
        cover_image_path = "outputs/images/hugegraph_cover_image.png"
        # 文章在 outputs/articles/，图片在 outputs/images/，使用相对路径
        cover_image_relative = "../images/hugegraph_cover_image.png"
        cover_placeholder_variants = [
            "[COVER_IMAGE_PLACEHOLDER]",
            "[封面图占位符]",
            "[封面图]",
        ]
        
        cover_markdown = ""
        if self.fm._resolve(cover_image_path).exists():
            cover_markdown = f"![Cover Image]({cover_image_relative})"
        else:
            cover_markdown = f"![Cover Image]({cover_image_relative})"
        
        for placeholder in cover_placeholder_variants:
            content = content.replace(placeholder, cover_markdown)

        link_markdown = self.link_collector.generate_link_collection()
        content = content.replace("## 链接集合占位符\n\n[链接集合占位符]", link_markdown.strip())
        content = content.replace("[链接集合占位符]", link_markdown.strip())
        content = content.replace("## 链接集合占位符", link_markdown.strip())
        return content

    def run(self, generate_cover: bool = True) -> None:
        """
        执行完整的毕业文章生成工作流
        
        Args:
            generate_cover: 是否生成封面图
        """
        try:
            # 步骤1: 生成封面图
            if generate_cover:
                try:
                    print("正在生成封面图...")
                    self.image_generator.generate_cover_image(style="formal")
                    print("封面图生成完成")
                except Exception as e:
                    print(f"警告: 封面图生成失败: {e}")
                    print("将继续执行文章生成...")

            # 步骤2: 生成文章内容
            try:
                print("正在生成文章内容...")
                result = self.article_generator.generate()
                print("文章内容生成完成")
            except Exception as e:
                print(f"错误: 文章生成失败: {e}")
                raise

            # 步骤3: 替换占位符
            try:
                print("正在替换占位符...")
                content = result.get("content", "")
                if not content:
                    raise ValueError("生成的文章内容为空")
                content = self._replace_placeholders(content)
                print("占位符替换完成")
            except Exception as e:
                print(f"警告: 占位符替换失败: {e}")
                # 即使占位符替换失败，也保存原始内容
                content = result.get("content", "")

            # 步骤4: 保存输出文件
            try:
                self.fm.write_text("outputs/articles/hugegraph_graduation_article.md", content)
                self.fm.write_json("outputs/data/article_outline.json", result.get("outline", {}))
                print("输出文件保存完成")
            except Exception as e:
                print(f"错误: 文件保存失败: {e}")
                raise

            print("=" * 60)
            print("工作流执行完成！")
            print(f"文章已保存到: outputs/articles/hugegraph_graduation_article.md")
            print(f"大纲已保存到: outputs/data/article_outline.json")
            print("=" * 60)

        except Exception as e:
            print("=" * 60)
            print(f"工作流执行失败: {e}")
            print("=" * 60)
            raise
